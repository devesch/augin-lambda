from time import time


class UsedCoupon:
    def __init__(self, coupon_code, user_id) -> None:
        self.pk = "coupon#" + coupon_code
        self.sk = "user#" + user_id
        self.coupon_code = coupon_code
        self.user_id = user_id
        self.created_at = str(time())
        self.entity = "coupon_used"
