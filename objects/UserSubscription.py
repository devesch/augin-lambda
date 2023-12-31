import time


class UserSubscription:
    def __init__(self, subscription_id, user_id) -> None:
        self.pk = "subscription#" + subscription_id
        self.sk = "subscription#" + subscription_id
        self.subscription_id = subscription_id
        self.subscription_user_id = user_id
        self.subscription_stripe_id = subscription_id
        self.subscription_plan_id = ""
        self.subscription_recurrency = ""
        self.subscription_status = ""
        self.subscription_price_id = ""
        self.subscription_price = ""
        self.subscription_currency = ""
        self.subscription_default_payment_method = ""
        self.subscription_last_order_id = ""
        self.subscription_valid_until = ""
        self.subscription_canceled_at = ""
        self.subscription_is_trial = False
        self.created_at = str(time.time())
        self.entity = "subscription"
