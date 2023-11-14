import time


class CancelSubscription:
    def __init__(self, subscription_id, user_id) -> None:
        self.pk = "cancel_subscription#" + subscription_id
        self.sk = "cancel_subscription#" + subscription_id
        self.cancel_subscription_subscription_id = subscription_id
        self.cancel_subscription_user_id = user_id
        self.cancel_subscription_found_a_better = False
        self.cancel_subscription_unhappy_service = False
        self.cancel_subscription_technical_problems = False
        self.cancel_subscription_too_expensive = False
        self.cancel_subscription_too_expensive = False
        self.cancel_subscription_not_using = False
        self.cancel_subscription_other_reasons = False
        self.cancel_subscription_text_area = ""
        self.created_at = str(time.time())
        self.entity = "cancel_subscription"
