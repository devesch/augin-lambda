from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
import json


class BackofficeCoupons(BackofficePage):
    name = "Backoffice - Cupons"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        backoffice_data = self.get_backoffice_data()

        if Validation().check_if_local_env():
            coupons, last_evaluated_key = Dynamo().query_paginated_all_coupons(limit=int(10000000))
            backoffice_data["backoffice_data_total_coupon_count"] = str(len(coupons))
            Dynamo().put_entity(backoffice_data)

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        coupons, last_evaluated_key = Dynamo().query_paginated_all_coupons(limit=int(self.user.user_pagination_count))
        html.esc("html_pagination", self.show_html_pagination(len(coupons), backoffice_data["backoffice_data_total_coupon_count"], "query_paginated_all_coupons", last_evaluated_key))
        html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
        html.esc("showing_total_count_val", len(coupons))

        html.esc("html_backoffice_coupons_table_rows", self.list_html_backoffice_coupons_table_rows(coupons))
        return str(html)

    def render_post(self):
        return self.render_get()
