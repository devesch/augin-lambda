from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
import json


class BackofficeCouponsHtml(BackofficePage):
    def run(self):
        last_evaluated_key = {}
        all_coupons = Dynamo().query_entity("coupon")
        filtered_coupons = []
        for coupon in all_coupons:
            if not self.post or (self.post["search_coupon"].lower() in coupon["coupon_name"].lower()) or (self.post["search_coupon"].lower() in coupon["coupon_code"].lower()):
                filtered_coupons.append(coupon)
        return {"success": self.list_html_backoffice_coupons_table_rows(filtered_coupons), "last_evaluated_key": json.dumps(last_evaluated_key), "query": "", "query_filter": "", "showing_total_count": len(filtered_coupons)}
