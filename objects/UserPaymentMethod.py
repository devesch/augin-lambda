import time


class UserPaymentMethod:
    def __init__(self, user_id, payment_method_id) -> None:
        self.pk = "user#" + user_id
        self.sk = "payment_method#" + payment_method_id
        self.payment_method_id = payment_method_id
        self.payment_method_user_id = user_id
        self.payment_method_type = ""
        self.payment_method_card = {}
        self.created_at = str(time.time())
        self.entity = "payment_method"
