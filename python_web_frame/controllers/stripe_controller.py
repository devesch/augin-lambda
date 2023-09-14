from os import environ
from json import load


stripe_token = "pk_test_51KUDNpA9OIVeHB9yQ6ngZSyKDmLUpgaq8iO10XRUy8bfLHzar7vgQ7AdXN6BFSUbTEe8O7DP3hDJ1DxFigcAbGzV00ZtwONkpc"
stripe_secret_key = "sk_test_51KUDNpA9OIVeHB9yBr8fiH7gVUhfggy4zFkJib2maUawYM4tSkRQ64swJwwx4pXFZ4U3O93qPEGRZzWW1agdeBd500ev6Lx5W5"
# stripe_webhook_key = "whsec_2dkGe8Hx2kduNIJr1XKkvR5BqHP1NKLX"


class StripeController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(StripeController, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.stripe = __import__("stripe")
        self.stripe.api_key = stripe_secret_key

    def create_stripe_customer(self, user):
        name = user.user_name
        phone = user.user_phone
        email = user.user_email
        address = {
            "city": user.user_address_data["user_street"],
            "line1": user.user_address_data["user_street"],
            "line2": user.user_address_data["user_complement"],
            "postal_code": user.user_address_data["user_zip_code"],
            "state": user.user_address_data["user_state"],
            "country": user.user_address_data["user_country"],
        }
        customer = self.stripe.Customer.create(email=email, name=name, phone=phone, address=address)
        return customer.stripe_id

    def get_stripe_customer(self, user_stripe_customer_id):
        return self.stripe.Customer.retrieve(user_stripe_customer_id)

    def update_stripe_customer(self, user_stripe_customer_id, user):
        name = user.user_name
        phone = user.user_phone
        email = user.user_email
        address = {
            "city": user.user_address_data["user_street"],
            "line1": user.user_address_data["user_street"],
            "line2": user.user_address_data["user_complement"],
            "postal_code": user.user_address_data["user_zip_code"],
            "state": user.user_address_data["user_state"],
            "country": user.user_address_data["user_country"],
        }
        self.stripe.Customer.modify(user_stripe_customer_id, email=email, name=name, phone=phone, address=address)

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

    def create_stripe_subscription(self, customer_id, price_id, user_cart):
        return self.stripe.Subscription.create(
            customer=customer_id,
            items=[
                {
                    "price": price_id,
                }
            ],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
            payment_settings={"payment_method_types": ["card"], "save_default_payment_method": "on_subscription"},
            metadata=user_cart,
        )

    def get_stripe_payment_intent(self, payment_intent_id):
        return self.stripe.PaymentIntent.retrieve(payment_intent_id)

    def get_stripe_subscription(self, subscription_id):
        return self.stripe.Subscription.retrieve(subscription_id)

    def cancel_stripe_subscription(self, subscription_id):
        return self.stripe.Subscription.delete(subscription_id)

    def convert_stripe_plan_interval_to_recurrence(self, stripe_plan_interval):
        if stripe_plan_interval == "month":
            return "monthly"
        if stripe_plan_interval == "year":
            return "annualy"

    def convert_stripe_status_code_to_status(self, stripe_status_code):
        if str(stripe_status_code) == "incomplete":
            return "pending"
        if str(stripe_status_code) == "requires_payment_method":
            return "pending"
        if str(stripe_status_code) == "succeeded":
            return "paid"
        else:
            return "stripe " + str(stripe_status_code)

    def convert_stripe_payment_code_to_method(self, stripe_payment_code):
        if str(stripe_payment_code[0]) == "card":
            return "credit_card"
        if str(stripe_payment_code[0]) == "pix":
            return "pix"

    def verify_stripe_signature(self, payload, sig_header, sandbox=False):
        endpoint_secret = self.stripe_sandbox_webhook_key
        if not sandbox:
            endpoint_secret = self.stripe_production_webhook_key
        try:
            event = self.stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            if event:
                return event
        except:
            return None

    def get_stripe_event(self, stripe_event_id):
        return self.stripe.Event.retrieve(stripe_event_id)

    def refunded_stripe_order(self, stripe_charge_id):
        return self.stripe.Refund.create(charge=stripe_charge_id)
