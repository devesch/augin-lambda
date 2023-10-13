from python_web_frame.controllers.stripe_controller import StripeController
from objects.Order import create_order_with_stripe_request_subscription
from python_web_frame.checkout_page import CheckoutPage
from utils.AWS.Dynamo import Dynamo


class CheckoutStripeGeneratePayload(CheckoutPage):
    def run(self):
        if not self.user:
            return {"error": "Nenhum usuário encontrado"}
        if not self.post.get("payment_type"):
            return {"error": "Nenhum tipo de compra enviado."}

        if self.post["payment_type"] == "subscription":
            plan = Dynamo().get_plan(self.post["plan_id"])
            try:
                stripe_request_payload = StripeController().create_subscription(self.user, plan, self.post["plan_recurrency"])
            except:
                self.user.recreate_stripe_user()
                stripe_request_payload = StripeController().create_subscription(self.user, plan, self.post["plan_recurrency"])
            create_order_with_stripe_request_subscription(self.user, plan, self.post["plan_recurrency"], stripe_request_payload)

        # if self.post["payment_recurrence"] == "unique":
        #     if self.user.user_address_data["user_country"] == "BR":
        #         stripe_request_payload = StripeController().create_stripe_payment_intent(self.user.user_cart_total_brl_price, "brl", "card", self.user.user_stripe_customer_id, self.user.user_cart)
        #     elif self.user.user_address_data["user_country"] != "BR":
        #         stripe_request_payload = StripeController().create_stripe_payment_intent(self.user.user_cart_total_usd_price, "usd", "card", self.user.user_stripe_customer_id, self.user.user_cart)
        #     payment_intent = StripeController().get_stripe_payment_intent(stripe_request_payload.stripe_id)
        #     self.create_order_with_stripe_payment_intent(self.user, payment_intent)
        #     return {"success": {"client_secret": stripe_request_payload.client_secret, "order_id": "stripe-" + stripe_request_payload.stripe_id}}

        return {"success": {"client_secret": stripe_request_payload["latest_invoice"]["payment_intent"]["client_secret"], "order_id": stripe_request_payload["latest_invoice"]["payment_intent"].stripe_id}}

    def get_subscription_from_user_cart(self, user_cart_updated):
        for product_address, product in user_cart_updated.items():
            return product

    def convert_price_to_s2p_float(self, string_price):
        return float(string_price[:-2] + "." + string_price[-2:])
