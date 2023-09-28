from python_web_frame.checkout_page import CheckoutPage
from python_web_frame.controllers.stripe_controller import StripeController
from objects.Order import Order, generate_order_descrimination
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
            self.create_order_with_stripe_subscription(self.user, plan, self.post["plan_recurrency"], stripe_request_payload)

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

    def create_order_with_stripe_subscription(self, user, plan, plan_recurrency, subscription):
        user.incrase_user_total_orders_count()
        new_order = Order(user.user_id, user.user_total_orders_count, subscription["latest_invoice"]["payment_intent"].stripe_id)
        new_order.order_status = StripeController().convert_stripe_status_code_to_status(subscription["status"])
        new_order.order_type = StripeController().convert_stripe_plan_interval_to_recurrence(subscription["plan"]["interval"])

        if self.user_cart_coupon_code:
            if plan_recurrency == "annually":
                new_order.order_sub_total_brl_price = plan["plan_price_annually_brl"]
                new_order.order_sub_total_usd_price = plan["plan_price_annually_usd"]

                order_brl_price, order_brl_discount = user.generate_plan_price_with_coupon_discount(plan, "annually", "brl")
                order_usd_price, order_usd_discount = user.generate_plan_price_with_coupon_discount(plan, "annually", "usd")
                new_order.order_brl_discount = order_brl_discount
                new_order.order_usd_discount = order_usd_discount
                new_order.order_brl_price = order_brl_price
                new_order.order_usd_price = order_usd_price

            if plan_recurrency == "monthly":
                new_order.order_sub_total_brl_price = plan["plan_price_monthly_brl_actual"]
                new_order.order_sub_total_usd_price = plan["plan_price_monthly_usd_actual"]

                order_brl_price, order_brl_discount = user.generate_plan_price_with_coupon_discount(plan, "monthly", "brl")
                order_usd_price, order_usd_discount = user.generate_plan_price_with_coupon_discount(plan, "monthly", "usd")
                new_order.order_brl_discount = order_brl_discount
                new_order.order_usd_discount = order_usd_discount
                new_order.order_brl_price = order_brl_price
                new_order.order_usd_price = order_usd_price

        else:
            if plan_recurrency == "annually":
                new_order.order_sub_total_brl_price = plan["plan_price_annually_brl_actual"]
                new_order.order_sub_total_usd_price = plan["plan_price_annually_usd_actual"]
                new_order.order_brl_price = plan["plan_price_annually_brl_actual"]
                new_order.order_usd_price = plan["plan_price_annually_usd_actual"]

            if plan_recurrency == "monthly":
                new_order.order_sub_total_brl_price = plan["plan_price_monthly_brl_actual"]
                new_order.order_sub_total_usd_price = plan["plan_price_monthly_usd_actual"]
                new_order.order_brl_price = plan["plan_price_monthly_brl_actual"]
                new_order.order_usd_price = plan["plan_price_monthly_usd_actual"]

        new_order.order_total_price = subscription["plan"]["amount_decimal"]
        new_order.order_currency = subscription["plan"]["currency"]
        new_order.order_installment_quantity = "1"
        new_order.order_payment_service = "stripe"
        new_order.order_payment_service_id = subscription["latest_invoice"]["payment_intent"].stripe_id
        new_order.order_payment_stripe_subscription_id = subscription.stripe_id
        new_order.order_plan_id = plan["plan_id"]
        new_order.order_plan_recurrency = plan_recurrency
        new_order.order_user_cart_cupom = self.user_cart_coupon_code
        new_order.order_descrimination = generate_order_descrimination(plan["plan_name_pt"], new_order.order_brl_price)
        Dynamo().put_entity(new_order.__dict__)
        self.increase_backoffice_data_total_count("order")

    # def create_order_with_stripe_payment_intent(self, user, payment_intent):
    #     new_order = Order(user.user_email, "stripe-" + payment_intent.stripe_id)
    #     new_order.order_status = StripeController().convert_stripe_status_code_to_status(payment_intent["status"])
    #     new_order.order_type = "unique"
    #     new_order.order_is_booth = user.user_cart_is_booth
    #     new_order.order_payment_method = payment_intent["payment_method_types"]
    #     new_order.order_sub_total_brl_price = user.user_cart_sub_total_brl_price
    #     new_order.order_sub_total_usd_price = user.user_cart_sub_total_usd_price
    #     new_order.order_brl_discount = user.user_cart_brl_discount
    #     new_order.order_usd_discount = user.user_cart_usd_discount
    #     new_order.order_brl_price = user.user_cart_total_brl_price
    #     new_order.order_usd_price = user.user_cart_total_usd_price
    #     new_order.order_total_price = str(payment_intent["amount"])
    #     new_order.order_currency = payment_intent["currency"]
    #     new_order.order_total_credits = user.user_cart_total_credits
    #     new_order.order_installment_quantity = "1"
    #     new_order.order_payment_service = "stripe"
    #     new_order.order_payment_service_id = payment_intent.stripe_id
    #     new_order.order_user_updated_cart_information = user.user_cart_updated
    #     new_order.order_user_cart_cupom = user.user_cart_cupom
    #     new_order.order_descrimination = self.utils.generate_order_descrimination(new_order.order_user_updated_cart_information, user.user_cart_total_brl_price)
    #     self.dynamo.put_entity(new_order.__dict__)
    #     self.increase_backoffice_data_total_count("order")
