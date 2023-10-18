from objects.Plan import generate_plan_price_with_coupon_discount
from utils.utils.Validation import Validation
import json

stripe_token = "pk_test_51KUDNpA9OIVeHB9yQ6ngZSyKDmLUpgaq8iO10XRUy8bfLHzar7vgQ7AdXN6BFSUbTEe8O7DP3hDJ1DxFigcAbGzV00ZtwONkpc"
stripe_secret_key = "sk_test_51KUDNpA9OIVeHB9yBr8fiH7gVUhfggy4zFkJib2maUawYM4tSkRQ64swJwwx4pXFZ4U3O93qPEGRZzWW1agdeBd500ev6Lx5W5"
stripe_webhook_key = "whsec_WKPU9mlyvPUzEFz1b5LJNixsrk6pgokG"


class StripeController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(StripeController, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.stripe = __import__("stripe")
        self.stripe.api_key = stripe_secret_key

    def attach_payment_method_to_customer(self, customer_id, payment_method_id):
        return self.stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)

    def get_payment_method(self, payment_method_id):
        return self.stripe.PaymentMethod.retrieve(payment_method_id)

    def delete_payment_method(self, payment_method_id):
        return self.stripe.PaymentMethod.detach(payment_method_id)

    def update_subscription_payment_method(self, subscription_id, payment_method_id):
        return self.stripe.Subscription.modify(subscription_id, default_payment_method=payment_method_id)

    def create_customer(self, user):
        address = {
            "city": user.user_address_data["user_street"],
            "line1": user.user_address_data["user_street"],
            "line2": user.user_address_data["user_complement"],
            "postal_code": user.user_address_data["user_zip_code"],
            "state": user.user_address_data["user_state"],
            "country": user.user_address_data["user_country"],
        }
        customer = self.stripe.Customer.create(email=user.user_email, name=user.user_name, phone=user.user_phone, address=address, preferred_locales=generate_preferred_locales(user.user_lang))
        return customer.stripe_id

    def get_stripe_customer(self, user_stripe_customer_id):
        return self.stripe.Customer.retrieve(user_stripe_customer_id)

    def update_customer(self, user_stripe_customer_id, user):
        address = {
            "city": user.user_address_data["user_street"],
            "line1": user.user_address_data["user_street"],
            "line2": user.user_address_data["user_complement"],
            "postal_code": user.user_address_data["user_zip_code"],
            "state": user.user_address_data["user_state"],
            "country": user.user_address_data["user_country"],
        }
        self.stripe.Customer.modify(id=user_stripe_customer_id, email=user.user_email, name=user.user_name, phone=user.user_phone, address=address, preferred_locales=generate_preferred_locales(user.user_lang))

    def delete_customer(self, user_stripe_customer_id):
        return self.stripe.Customer.delete(user_stripe_customer_id)

    def create_product(self, product, type="plan"):
        active = True
        if type == "plan":
            if not product["plan_available_for_purchase"]:
                active = False
            self.stripe.Product.create(id=product["plan_id"], name=product["plan_name_pt"], active=active)

    def get_product(self, product_id):
        return self.stripe.Product.retrieve(product_id)

    def update_product(self, product, type="plan"):
        active = True
        if type == "plan":
            if not product["plan_available_for_purchase"]:
                active = False
            self.stripe.Product.modify(product["plan_id"], name=product["plan_name_pt"], active=active)

    def delete_stripe_product(self, product_address):
        return self.stripe.Product.delete(product_address)

    def create_price(self, product_address, currency, amount, interval):
        price = self.stripe.Price.create(unit_amount=int(amount), currency=currency, recurring={"interval": interval}, product=product_address)
        return price.stripe_id

    def get_price(self, product_stripe_price_id):
        return self.stripe.Price.retrieve(product_stripe_price_id)

    def delete_price(self, product_stripe_price_id):
        return self.stripe.Price.modify(product_stripe_price_id, active=False)

    def create_stripe_payment_intent(self, amount, currency, payment_method, customer_id, user_cart):
        return self.stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method_types=[payment_method],
            customer=customer_id,
            metadata=user_cart,
        )

    def create_subscription(self, user, plan, plan_recurrency):
        payment_method_types = []

        price_id = self.generate_price_id(user, plan, plan_recurrency)
        payment_method_types = self.generate_payment_method_types(user, plan, plan_recurrency)

        if user.user_cart_coupon_code:
            new_subscription_price, coupon_discount_value = generate_plan_price_with_coupon_discount(plan, user.user_cart_coupon_code, plan_recurrency, user.user_cart_currency)
            if new_subscription_price:
                price_id = self.create_price(plan["plan_id"], user.user_cart_currency, new_subscription_price, self.convert_recurrence_stripe_plan_interval(plan_recurrency))

        return self.stripe.Subscription.create(
            customer=user.user_stripe_customer_id,
            items=[
                {
                    "price": price_id,
                }
            ],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
            payment_settings={"payment_method_types": payment_method_types, "save_default_payment_method": "on_subscription"},
            metadata={"user_id": user.user_id, "plan_recurrency": plan_recurrency, "coupon_code": user.user_cart_coupon_code, "plan_id": plan["plan_id"], "plan": self.compress_plan_data(plan)},
        )

    def get_payment_intent(self, payment_intent_id):
        return self.stripe.PaymentIntent.retrieve(payment_intent_id)

    def get_invoice(self, invoice_id):
        return self.stripe.Invoice.retrieve(invoice_id)

    def get_subscription(self, subscription_id):
        stripe_subscription = self.stripe.Subscription.retrieve(subscription_id)
        if stripe_subscription["metadata"].get("plan"):
            if Validation().check_if_is_b64_encoded(stripe_subscription["metadata"]["plan"]):
                stripe_subscription["metadata"]["plan"] = self.decompress_plan_data(stripe_subscription["metadata"]["plan"])
        return stripe_subscription

    def cancel_subscription(self, subscription_id):
        return self.stripe.Subscription.delete(subscription_id)

    def convert_stripe_plan_interval_to_recurrence(self, stripe_plan_interval):
        if stripe_plan_interval == "month":
            return "monthly"
        if stripe_plan_interval == "year":
            return "annually"

    def convert_recurrence_stripe_plan_interval(self, stripe_plan_interval):
        if stripe_plan_interval == "monthly":
            return "month"
        if stripe_plan_interval == "annually":
            return "year"

    def convert_stripe_status_code_to_status(self, stripe_status_code):
        if str(stripe_status_code) == "incomplete":
            return "pending"
        if str(stripe_status_code) == "requires_payment_method":
            return "pending"
        if str(stripe_status_code) == "succeeded":
            return "paid"
        else:
            return str(stripe_status_code)

    def verify_stripe_signature(self, payload, sig_header):
        try:
            event = self.stripe.Webhook.construct_event(payload, sig_header, stripe_webhook_key)
            if event:
                return event
        except:
            return None

    def get_stripe_event(self, stripe_event_id):
        return self.stripe.Event.retrieve(stripe_event_id)

    def refunded_order(self, stripe_charge_id):
        return self.stripe.Refund.create(charge=stripe_charge_id)

    def remove_coupon_from_subscription(self, user, stripe_subscription):
        price_id = self.generate_price_id(user, stripe_subscription["metadata"]["plan"], stripe_subscription["metadata"]["plan_recurrency"])
        new_metadata = {"user_id": stripe_subscription["metadata"]["user_id"], "plan_recurrency": stripe_subscription["metadata"]["plan_recurrency"], "coupon_code": "", "plan_id": stripe_subscription["metadata"]["plan"]["plan_id"], "plan": self.compress_plan_data(stripe_subscription["metadata"]["plan"])}

        return self.stripe.Subscription.modify(
            stripe_subscription["id"],
            cancel_at_period_end=False,
            proration_behavior="none",
            items=[
                {
                    "id": stripe_subscription["items"]["data"][0].id,
                    "price": price_id,
                }
            ],
            metadata=new_metadata,
        )

    def generate_price_id(self, user, plan, plan_recurrency):
        if plan_recurrency == "annually":
            if user.user_cart_currency == "brl":
                price_id = plan["plan_price_annually_brl_actual_stripe_id"]
            if user.user_cart_currency == "usd":
                price_id = plan["plan_price_annually_usd_actual_stripe_id"]

        if plan_recurrency == "monthly":
            if user.user_cart_currency == "brl":
                price_id = plan["plan_price_monthly_brl_actual_stripe_id"]
            if user.user_cart_currency == "usd":
                price_id = plan["plan_price_monthly_usd_actual_stripe_id"]

        return price_id

    def generate_payment_method_types(self, user, plan, plan_recurrency):
        payment_method_types = []

        if plan_recurrency == "annually":
            if user.user_cart_currency == "brl":
                if plan["plan_annually_boleto_payment_method"]:
                    payment_method_types.append("boleto")
                # if plan["plan_annually_pix_payment_method"]:
                #     payment_method_types.append("pix")
            if plan["plan_annually_card_payment_method"]:
                payment_method_types.append("card")

        if plan_recurrency == "monthly":
            if user.user_cart_currency == "brl":
                if plan["plan_monthly_boleto_payment_method"]:
                    payment_method_types.append("boleto")
                # if plan["plan_monthly_pix_payment_method"]:
                #     payment_method_types.append("pix")
            if plan["plan_monthly_card_payment_method"]:
                payment_method_types.append("card")

        return payment_method_types

    def compress_plan_data(self, plan):
        import zlib
        import base64

        string_plan_data = json.dumps(
            {
                "plan_id": plan["plan_id"],
                "plan_name_pt": plan["plan_name_pt"],
                "plan_price_annually_brl": plan["plan_price_annually_brl"],
                "plan_price_annually_usd": plan["plan_price_annually_usd"],
                "plan_price_monthly_brl": plan["plan_price_monthly_brl"],
                "plan_price_monthly_usd": plan["plan_price_monthly_usd"],
                "plan_price_annually_brl_actual": plan["plan_price_annually_brl_actual"],
                "plan_price_annually_usd_actual": plan["plan_price_annually_usd_actual"],
                "plan_price_monthly_brl_actual": plan["plan_price_monthly_brl_actual"],
                "plan_price_monthly_usd_actual": plan["plan_price_monthly_usd_actual"],
                "plan_price_annually_brl_actual_stripe_id": plan["plan_price_annually_brl_actual_stripe_id"],
                "plan_price_annually_usd_actual_stripe_id": plan["plan_price_annually_usd_actual_stripe_id"],
                "plan_price_monthly_brl_actual_stripe_id": plan["plan_price_monthly_brl_actual_stripe_id"],
                "plan_price_monthly_usd_actual_stripe_id": plan["plan_price_monthly_usd_actual_stripe_id"],
            }
        )

        return base64.b64encode(zlib.compress(string_plan_data.encode("utf-8"))).decode("utf-8")

    def decompress_plan_data(self, compressed_plan_data):
        import zlib
        import base64

        decompressed_data = base64.b64decode(compressed_plan_data)
        original_string_data = zlib.decompress(decompressed_data)
        return json.loads(original_string_data.decode("utf-8"))


def generate_preferred_locales(user_lang):
    if user_lang == "pt":
        return ["pt-BR"]
    elif user_lang == "es":
        return ["es-ES"]
    else:
        return ["en-US"]
