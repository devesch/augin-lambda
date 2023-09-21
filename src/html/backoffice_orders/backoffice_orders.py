from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
import json


class BackofficeOrders(BackofficePage):
    name = "Backoffice - Pagamentos"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)

        backoffice_data = self.get_backoffice_data()
        if self.post.get("showing_total_count"):
            if self.path.get("order_status") and self.path.get("order_status") != "all":
                orders, last_evaluated_key = Dynamo().query_paginated_all_orders_from_status(self.path["order_status"], limit=int(self.post["showing_total_count"]))
            else:
                orders, last_evaluated_key = Dynamo().query_paginated_all_orders(limit=int(self.post["showing_total_count"]))
        else:
            if self.path.get("order_status") and self.path.get("order_status") != "all":
                orders, last_evaluated_key = Dynamo().query_paginated_all_orders_from_status(self.path["order_status"], limit=int(self.user.user_pagination_count))
            else:
                orders, last_evaluated_key = Dynamo().query_paginated_all_orders(limit=int(self.user.user_pagination_count))

        if self.path.get("order_status"):
            html.esc("pre_sel_" + self.path["order_status"] + "_val", 'selected="selected"')
            query = "query_paginated_all_orders_from_status"
        else:
            query = "query_paginated_all_orders"

        html.esc("html_pagination", self.show_html_pagination(len(orders), backoffice_data["backoffice_data_total_order_count"], query, last_evaluated_key, self.path.get("order_status", "")))
        html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
        html.esc("showing_total_count_val", len(orders))

        html.esc("html_backoffice_orders_table_rows", self.list_html_backoffice_orders_table_rows(orders))
        return str(html)

    def render_post(self):
        return self.render_get()
