from python_web_frame.base_page import User, BasePage
from python_web_frame.controllers.billing_controller import BillingController
from python_web_frame.controllers.stripe_controller import StripeController
from utils.utils.Validation import Validation
from objects.Order import Order
from utils.AWS.Dynamo import Dynamo


class CheckoutStripeWebHook(BasePage):
    def run(self):
        if not Validation().check_if_local_env():
            verified_stripe_event = StripeController().verify_stripe_signature(self.event.body, self.event.headers["stripe-signature"])
            if not verified_stripe_event:
                return {"error": "Evento não verificado pelo stripe."}

        if self.post["type"] == "payment_intent.succeeded":
            stripe_customer = StripeController().get_stripe_customer(self.post["data"]["object"]["customer"])
            self.user = self.load_user(stripe_customer["email"])
            order = Dynamo().get_order(self.post["data"]["object"]["id"])
            user_stripe_subscription = None
            if not order and self.post["data"]["object"]["description"] == "Subscription update":
                self.utils.send_payload_email(self.event, "MAGIPIX SUBSCRIPTION STRIPE PAYMENT")
                if self.user.user_subscription:  ### TODO MAKE MORE CHECKS TO MAKE SURE SUBSCRIPTION UPDATE IS FROM THE SAME SUB_ID, CHECK WHEN CHARGE ID COMES
                    user_stripe_subscription = StripeController().get_stripe_subscription(self.user.user_subscription["subscription_stripe_id"])
                    user_first_order_from_subscription = self.get_user_first_order_from_subscription(self.user.user_email, self.user.user_subscription["subscription_last_order_id"])
                    product_subscription = self.user.user_subscription["subscription_product"]
                    self.create_order_from_subscription_update(self.user, user_stripe_subscription, self.post["data"]["object"], user_first_order_from_subscription)
                    order = self.dynamo.get_order(self.user.user_email, "stripe-" + self.post["data"]["object"]["id"])

            Dynamo().update_entity(order, "order_status", StripeController().convert_stripe_status_code_to_status(self.post["data"]["object"]["status"]))
            if order["order_type"] == "unique":
                raise Exception("TODO SINGLE PURCHASE")
            else:
                if not user_stripe_subscription:
                    user_stripe_subscription = StripeController().get_stripe_subscription(order["order_payment_stripe_subscription_id"])
                self.user.update_subscription(order, user_stripe_subscription)
            if order["order_user_cart_cupom"]:
                self.mark_cupom_as_used_and_update_cupom_count(order, self.user.user_email)
            if order["order_currency"] == "brl":
                BillingController().generate_bill_of_sale(self.user, order)
            elif order["order_currency"] == "usd":
                BillingController().generate_international_pdf_bill_of_sale(order)
            self.send_payment_success_email(order)
            return {"success": "Evento payment_intent.succeeded tratado."}

        elif self.post["type"] == "charge.succeeded":
            stripe_customer = StripeController().get_stripe_customer(self.post["data"]["object"]["customer"])
            self.user = self.load_user(stripe_customer["email"])
            order = self.dynamo.get_order(self.user.user_email, "stripe-" + self.post["data"]["object"]["payment_intent"])
            if not order:
                import time

                time.sleep(15)
                order = self.dynamo.get_order(self.user.user_email, "stripe-" + self.post["data"]["object"]["payment_intent"])
            self.dynamo.update_entity(order, "order_payment_stripe_charge_id", self.post["data"]["object"]["id"])
            return {"success": "Evento charge.succeeded tratado."}

        return {"success": "Evento não tratado."}

    def get_user_first_order_from_subscription(self, user_email, subscription_last_order_id):
        return self.dynamo.get_order(user_email, subscription_last_order_id)

    def get_subscription_from_user_cart(self, user_cart_updated):
        for product_address, product in user_cart_updated.items():
            return product

    def calculate_credits_to_add_to_user(self, order_user_updated_cart_information):
        new_credits = 0
        for product_address, product in order_user_updated_cart_information.items():
            new_credits += int(product["product_credits"]) * int(product["product_quantity"])
        return str(new_credits)

    def create_order_from_subscription_update(self, user, subscription, payment_intent, user_first_order_from_subscription):
        new_order = Order(user.user_email, "stripe-" + payment_intent["id"])
        new_order.order_status = StripeController().convert_stripe_status_code_to_status(payment_intent["status"])
        new_order.order_type = StripeController().convert_stripe_plan_interval_to_recurrence(subscription["plan"]["interval"])
        new_order.order_payment_method = StripeController().convert_stripe_payment_code_to_method(subscription["payment_settings"]["payment_method_types"])
        new_order.order_sub_total_brl_price = user_first_order_from_subscription["order_sub_total_brl_price"]
        new_order.order_sub_total_usd_price = user_first_order_from_subscription["order_sub_total_usd_price"]
        new_order.order_brl_discount = user_first_order_from_subscription["order_brl_discount"]
        new_order.order_usd_discount = user_first_order_from_subscription["order_usd_discount"]
        new_order.order_brl_price = user_first_order_from_subscription["order_brl_price"]
        new_order.order_usd_price = user_first_order_from_subscription["order_usd_price"]
        new_order.order_total_price = subscription["plan"]["amount_decimal"]
        new_order.order_currency = subscription["plan"]["currency"]
        new_order.order_total_credits = user_first_order_from_subscription["order_total_credits"]
        new_order.order_installment_quantity = "1"
        new_order.order_payment_service = "stripe"
        new_order.order_payment_service_id = payment_intent["id"]
        new_order.order_payment_stripe_subscription_id = subscription.stripe_id
        new_order.order_user_updated_cart_information = user_first_order_from_subscription["order_user_updated_cart_information"]
        new_order.order_user_cart_cupom = user_first_order_from_subscription["order_user_cart_cupom"]
        new_order.order_descrimination = self.utils.generate_order_descrimination(user_first_order_from_subscription["order_user_updated_cart_information"], user_first_order_from_subscription["order_brl_price"])
        self.dynamo.put_entity(new_order.__dict__)
        self.increase_backoffice_data_total_count("order")
