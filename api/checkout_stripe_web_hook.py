from python_web_frame.controllers.billing_controller import BillingController
from python_web_frame.controllers.stripe_controller import StripeController
from objects.Order import create_order_with_stripe_subscription_updated
from objects.BackofficeData import increase_backoffice_data_total_count
from objects.Coupon import generate_coupon_cycle_applications
from objects.UserPaymentMethod import UserPaymentMethod
from objects.RecurrenceFailure import RecurrenceFailure
from python_web_frame.base_page import BasePage
from utils.utils.Validation import Validation
from utils.utils.ReadWrite import ReadWrite
from utils.utils.StrFormat import StrFormat
from utils.AWS.Dynamo import Dynamo
from objects.User import load_user
from utils.AWS.Ses import Ses
import time
import json

### TODO REMOVE BEFORE PROD
working_on_sub_id = "sub_1O1tpMA9OIVeHB9ymACRQukE"


class CheckoutStripeWebHook(BasePage):
    def run(self):
        if not Validation().check_if_local_env():
            verified_stripe_event = StripeController().verify_stripe_signature(self.event.body, self.event.headers["stripe-signature"])
            if not verified_stripe_event:
                return {"error": "Evento não verificado pelo stripe."}

        return getattr(self, self.post["type"].replace(".", "_"))()

    def payment_intent_succeeded(self):
        stripe_customer = StripeController().get_stripe_customer(self.post["data"]["object"]["customer"])
        self.user = load_user(stripe_customer["email"])
        order = Dynamo().get_order(self.post["data"]["object"]["id"])
        stripe_subscription = None
        if not order and self.post["data"]["object"]["description"] == "Subscription update":
            invoice = StripeController().get_invoice(self.post["data"]["object"]["invoice"])
            stripe_subscription = StripeController().get_subscription(working_on_sub_id)
            ### TODO CHANGE SUB
            # stripe_subscription = StripeController().get_subscription(self.user.user_subscription_id)
            # stripe_subscription = StripeController().get_subscription(invoice['subscription'])
            create_order_with_stripe_subscription_updated(self.user, stripe_subscription["metadata"]["plan"], stripe_subscription["metadata"]["plan_recurrency"], stripe_subscription, self.post["data"]["object"], invoice)
            order = Dynamo().get_order(self.post["data"]["object"]["id"])

        Dynamo().update_entity(order, "order_status", StripeController().convert_stripe_status_code_to_status(self.post["data"]["object"]["status"]))
        Dynamo().update_entity(order, "order_paid_at", str(time.time()))

        if self.post["data"]["object"]["status"] == "succeeded":
            if order["order_type"] == "unique":
                raise Exception("TODO SINGLE PURCHASE")
            else:
                if not stripe_subscription:
                    stripe_subscription = StripeController().get_subscription(order["order_payment_stripe_subscription_id"])
                user_subscription = Dynamo().get_subscription(self.user.user_subscription_id)
                if user_subscription and (user_subscription.get("subscription_status") == "active") and (stripe_subscription.stripe_id != user_subscription["subscription_id"]):
                    self.user.cancel_current_subscription()
                self.user.update_subscription(order, stripe_subscription)

            if order["order_nfse_status"] != "issued":
                if order["order_currency"] == "brl":
                    BillingController().generate_bill_of_sale(self.user, order)
                elif order["order_currency"] == "usd":
                    BillingController().generate_international_pdf_bill_of_sale(order)

            if order["order_user_cart_coupon_code"]:
                coupon = Dynamo().get_coupon(order["order_user_cart_coupon_code"])
                coupon_cycle_applications = generate_coupon_cycle_applications(coupon, user_subscription["subscription_recurrency"])
                if int(order["order_installment_quantity"]) >= int(coupon_cycle_applications):
                    StripeController().remove_coupon_from_subscription(self.user, stripe_subscription)

                if self.post["data"]["object"]["description"] != "Subscription update":
                    self.mark_coupon_as_used_and_update_coupon_count(order, self.user.user_id)
                    self.user.remove_user_cart_coupon_code()

                self.send_payment_success_email(order)

        # raise Exception("TODO PAYMENT SUCCESS")
        return {"success": "Evento payment_intent_succeeded tratado."}

    def charge_succeeded(self):
        stripe_customer = StripeController().get_stripe_customer(self.post["data"]["object"]["customer"])
        self.user = load_user(stripe_customer["email"])
        order = Dynamo().get_order(self.post["data"]["object"]["payment_intent"])
        if not order:
            for x in range(15):
                time.sleep(1)
                order = Dynamo().get_order(self.post["data"]["object"]["payment_intent"])
                if order:
                    break
        Dynamo().update_entity(order, "order_payment_stripe_charge_id", self.post["data"]["object"]["id"])
        Dynamo().update_entity(order, "order_payment_stripe_receipt_url", self.post["data"]["object"]["receipt_url"])
        Dynamo().update_entity(order, "order_payment_method", self.post["data"]["object"]["payment_method_details"]["type"])

        payment_method = Dynamo().get_payment_method(self.user.user_id, self.post["data"]["object"]["payment_method"])
        if not payment_method:
            payment_method = UserPaymentMethod(self.user.user_id, self.post["data"]["object"]["payment_method"]).__dict__

        payment_method["payment_method_type"] = self.post["data"]["object"]["payment_method_details"]["type"]
        if self.post["data"]["object"]["payment_method_details"]["type"] == "card":
            payment_method["payment_method_card"] = {}
            for key, val in self.post["data"]["object"]["payment_method_details"]["card"].items():
                if type(val) == str or type(val) == int:
                    payment_method["payment_method_card"][key] = str(val)

        Dynamo().put_entity(payment_method)
        return {"success": "Evento charge_succeeded tratado."}

    def payment_intent_payment_failed(self):
        order = Dynamo().get_order(self.post["data"]["object"]["id"])
        failure_in_recurrence = False
        if not order:
            failure_in_recurrence = True
            stripe_customer = StripeController().get_stripe_customer(self.post["data"]["object"]["customer"])
            self.user = load_user(stripe_customer["email"])
            invoice = StripeController().get_invoice(self.post["data"]["object"]["invoice"])
            stripe_subscription = StripeController().get_subscription(invoice["subscription"])
            create_order_with_stripe_subscription_updated(self.user, stripe_subscription["metadata"]["plan"], stripe_subscription["metadata"]["plan_recurrency"], stripe_subscription, self.post["data"]["object"], invoice)
            order = Dynamo().get_order(self.post["data"]["object"]["id"])
            if self.user.user_subscription_id and (invoice["subscription"] == self.user.user_subscription_id):
                self.user.update_subscription(order, stripe_subscription)

        Dynamo().update_entity(order, "order_last_error_code", self.post["data"]["object"]["last_payment_error"]["code"])
        Dynamo().update_entity(order, "order_last_error_message", self.post["data"]["object"]["last_payment_error"]["message"])
        Dynamo().update_entity(order, "order_status", "error")

        if failure_in_recurrence:
            recurrence_failure = RecurrenceFailure(self.user.user_id, order["order_id"]).__dict__
            Dynamo().put_entity(recurrence_failure)
            increase_backoffice_data_total_count("recurrence_failure")

        # raise Exception("TODO PAYMENT FAILED")
        return {"success": "Evento payment_intent_payment_failed tratado."}

    def payment_intent_requires_action(self):
        order = Dynamo().get_order(self.post["data"]["object"]["id"])
        Dynamo().update_entity(order, "order_payment_method", "boleto")
        Dynamo().update_entity(order, "order_payment_stripe_boleto_url", self.post["data"]["object"]["next_action"]["boleto_display_details"]["pdf"])
        Dynamo().update_entity(order, "order_status", "waiting_payment")
        return {"success": "Evento payment_intent_requires_action tratado."}

    def customer_subscription_updated(self):
        user_stripe_subscription = StripeController().get_subscription(self.post["data"]["object"]["id"])
        stripe_customer = StripeController().get_stripe_customer(user_stripe_subscription["customer"])
        self.user = load_user(stripe_customer["email"])
        invoice = StripeController().get_invoice(user_stripe_subscription["latest_invoice"])
        order = Dynamo().get_order(invoice["payment_intent"])
        self.user.update_subscription(order, user_stripe_subscription)
        return {"success": "Evento customer_subscription_updated tratado."}

    ######################################################################################################

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

    def send_payment_success_email(self, order):
        html = ReadWrite().read_html("main/emails/html_payment_success_email")
        html.esc("user_email_val", self.user.user_email)
        html.esc("user_name_val", self.user.user_name)
        html.esc("order_currency_val", StrFormat().format_currency_to_symbol(order["order_currency"]))
        html.esc("order_total_price_val", StrFormat().format_to_money(order["order_total_price"], order["order_currency"]))
        html.esc("order_id_val", order["order_id"])
        ### TODO EM PROD ADD EVERYONES EMAILS
        Ses().send_email("eugenio@devesch.com.br", body_html=str(html), body_text=str(html), subject_data="Pagamento realizado com sucesso")

    def mark_coupon_as_used_and_update_coupon_count(self, order, user_id):
        from objects.UsedCoupon import UsedCoupon
        from objects.Coupon import increase_coupon_actual_uses_count

        used_coupon = UsedCoupon(order["order_user_cart_coupon_code"], user_id)
        Dynamo().put_entity(used_coupon.__dict__)
        cupom = Dynamo().get_coupon(order["order_user_cart_coupon_code"])
        increase_coupon_actual_uses_count(cupom)
