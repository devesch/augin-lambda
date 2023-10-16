from utils.AWS.Dynamo import Dynamo
import time


class Coupon:
    def __init__(self, coupon_code="") -> None:
        self.pk = "coupon#" + coupon_code
        self.sk = "coupon#" + coupon_code
        self.coupon_code = coupon_code

        self.coupon_name = ""
        self.coupon_description = ""
        self.coupon_available_for_limited_time = False
        self.coupon_start_date = ""
        self.coupon_end_date = ""
        self.coupon_has_limited_uses_count = False
        self.coupon_actual_uses_count = "0"
        self.coupon_maxium_uses_count = "0"
        self.coupon_discount_type = "total"  # total/percentage
        self.coupon_brl_discount = "0"
        self.coupon_usd_discount = "0"
        self.coupon_percentage_discount = "1"
        self.coupon_recurrence_months = "1"
        self.coupon_available_monthly = False
        self.coupon_available_annually = False
        self.coupon_available_in_brl = False
        self.coupon_available_in_usd = False
        self.coupons_plans_ids = []
        self.created_at = str(time.time())
        self.entity = "coupon"


def increase_coupon_actual_uses_count(coupon):
    coupon["coupon_actual_uses_count"] = str(int(coupon["coupon_actual_uses_count"]) + 1)
    Dynamo().update_entity(coupon, "coupon_actual_uses_count", coupon["coupon_actual_uses_count"])


def generate_coupon_cycle_applications(coupon, plan_recurrence):
    import math

    cycle_applications = "1"
    if plan_recurrence == "monthly":
        cycle_applications = str(math.ceil(int(coupon["coupon_recurrence_months"] / 1)))
    if plan_recurrence == "annually":
        cycle_applications = str(math.ceil(int(coupon["coupon_recurrence_months"]) / 12))

    return cycle_applications
