from python_web_frame.controllers.billing_controller import BillingController
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.base_page import BasePage
from objects.BackofficeData import get_backoffice_data, increase_backoffice_data_total_count, fix_backoffice_data_total_count
from objects.User import load_user
from objects.CartAbandonment import CartAbandonment
from utils.utils.Validation import Validation
from utils.AWS.Dynamo import Dynamo
from utils.Config import lambda_constants
from datetime import datetime
import time


class LambdaPeriodicActions(BasePage):
    def run(self):
        if not Validation().check_if_local_env():
            if not self.post.get("lambda_periodic_actions_key"):
                return {"error": "Nenhum lambda_periodic_actions_key encontrada no post"}
            if self.post["lambda_periodic_actions_key"] != lambda_constants["lambda_periodic_actions_key"]:
                return {"error": "lambda_periodic_actions_key incorreta"}

        self.check_for_cart_abandonments()
        BillingController().check_and_issued_not_issued_bill_of_sales()
        self.check_for_models_with_error_still_processing()
        if datetime.today().day == 1:
            BillingController().generate_and_send_orders_nfses()
            fix_backoffice_data_total_count(get_backoffice_data())
        return {"success": "Todas as periodic actions foram realizadas"}

    def check_for_cart_abandonments(self):
        checked_pending_users = []
        pending_orders_from_last_24h = Dynamo().query_all_pending_orders_from_last_24h()
        if pending_orders_from_last_24h:
            for pending_order in pending_orders_from_last_24h:
                if pending_order["order_user_id"] not in checked_pending_users and ((float(pending_order["created_at"]) + 3600) < time.time()):
                    checked_pending_users.append(pending_order["order_user_id"])
                    order_user = load_user(pending_order["order_user_id"])
                    if order_user:
                        if (order_user.user_subscription_status == "none") or (order_user.user_subscription_status == "canceled"):
                            cart_abandonment = CartAbandonment(order_user.user_id, pending_order["order_id"]).__dict__
                            Dynamo().put_entity(cart_abandonment)
                            increase_backoffice_data_total_count("cart_abandonment")

    def check_for_models_with_error_still_processing(self):
        models_processing, last_evaluated_key = Dynamo().query_paginated_all_models_by_state("in_processing", limit=10000000)
        for model in models_processing:
            if ModelController().check_if_model_in_processing_is_with_error(model["model_processing_started_at"]):
                ModelController().mark_model_as_error(model, "Processamento interminável")
