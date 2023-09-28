from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
import json


class BackofficeOrders(BackofficePage):
    name = "Backoffice - Pagamentos"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        backoffice_data = self.get_backoffice_data()

        if Validation().check_if_local_env():
            orders, last_evaluated_key = Dynamo().query_paginated_all_orders(limit=int(10000000))
            backoffice_data["backoffice_data_total_order_count"] = str(len(orders))
            Dynamo().put_entity(backoffice_data)

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)

        orders, last_evaluated_key = Dynamo().query_paginated_all_orders(limit=int(self.user.user_pagination_count))
        html.esc("html_pagination", self.show_html_pagination(len(orders), backoffice_data["backoffice_data_total_order_count"], "query_paginated_all_orders", last_evaluated_key, self.path.get("order_status", "")))
        html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
        html.esc("showing_total_count_val", len(orders))

        html.esc("html_backoffice_orders_table_rows", self.list_html_backoffice_orders_table_rows(orders))
        return str(html)

    def render_post(self):
        return self.render_get()
