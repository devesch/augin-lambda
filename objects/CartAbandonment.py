import time


class CartAbandonment:
    def __init__(self, user_id, cart_abandonment_id) -> None:
        self.pk = "user#" + user_id
        self.sk = "cart_abandonment#" + cart_abandonment_id

        self.cart_abandonment_user_id = user_id
        self.cart_abandonment_id = cart_abandonment_id
        self.cart_abandonment_order_id = cart_abandonment_id

        self.created_at = str(time.time())
        self.entity = "cart_abandonment"
