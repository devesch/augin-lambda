from python_web_frame.controllers.billing_controller import BillingController
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.base_page import BasePage
from objects.BackofficeData import get_backoffice_data
from utils.utils.Validation import Validation
from utils.AWS.Dynamo import Dynamo
from utils.Config import lambda_constants
from datetime import datetime


class LambdaPeriodicActions(BasePage):
    def run(self):
        if not Validation().check_if_local_env():
            if not self.post.get("lambda_periodic_actions_key"):
                return {"error": "Nenhum lambda_periodic_actions_key encontrada no post"}
            if self.post["lambda_periodic_actions_key"] != lambda_constants["lambda_periodic_actions_key"]:
                return {"error": "lambda_periodic_actions_key incorreta"}

        BillingController().check_and_issued_not_issued_bill_of_sales()
        self.check_for_models_with_error_still_processing()
        # TODO CHANGE FIX TOTAL COUNT TO MONTH
        self.fix_total_count()
        if datetime.today().day == 1:
            BillingController().generate_and_send_orders_nfses()
            # self.fix_total_count()
        return {"success": "all periodic actions completed"}

    def check_for_models_with_error_still_processing(self):
        models_processing, last_evaluated_key = Dynamo().query_paginated_all_models_by_state("in_processing", limit=10000000)
        for model in models_processing:
            if ModelController().check_if_model_in_processing_is_with_error(model["model_processing_started_at"]):
                ModelController().mark_model_as_error(model, "Processamento interminável")

    def fix_total_count(self):

        ## TODO FIX
        all_users = Dynamo().query_entity("user")
        # for user in all_users:
        #     pending_projects, last_evaluated_key = self.dynamo.query_paginated_projects_from_user(user["user_email"], "pending", limit=100000)
        #     self.dynamo.update_entity(user, "user_total_count_pending_projects", str(len(pending_projects)))
        #     published_project, last_evaluated_key = self.dynamo.query_paginated_projects_from_user(user["user_email"], "published", limit=100000)
        #     self.dynamo.update_entity(user, "user_total_count_published_projects", str(len(published_project)))
        #     credits_modifications, last_evaluated_key = self.dynamo.query_paginated_all_users_credits_modifications(user["user_email"], limit=100000)
        #     self.dynamo.update_entity(user, "user_total_count_credits_modifications", str(len(credits_modifications)))

        all_models = Dynamo().query_entity("model")
        # for project in all_projects:
        #     project_balances, last_evaluated_key = self.dynamo.query_paginated_project_balance(project["project_id"], last_evaluated_key=None, limit=100000)
        #     self.dynamo.update_entity(project, "project_total_project_balance_count", str(len(project_balances)))

        all_orders = Dynamo().query_entity("order")
        all_coupons = Dynamo().query_entity("coupons")
        all_products = Dynamo().query_entity("product")

        backoffice_data = get_backoffice_data()
        backoffice_data["backoffice_data_total_user_count"] = str(len(all_users))
        backoffice_data["backoffice_data_total_order_count"] = str(len(all_orders))
        backoffice_data["backoffice_data_total_model_count"] = str(len(all_models))
        backoffice_data["backoffice_data_total_coupon_count"] = str(len(all_coupons))
        backoffice_data["backoffice_data_total_product_count"] = str(len(all_products))
        Dynamo().put_entity(backoffice_data)
