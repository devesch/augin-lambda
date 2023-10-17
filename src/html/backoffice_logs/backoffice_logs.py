from python_web_frame.backoffice_page import BackofficePage
from objects.BackofficeData import get_backoffice_data
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
import json


class BackofficeLogs(BackofficePage):
    name = "Backoffice - Logs"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        # backoffice_data = get_backoffice_data()

        # if Validation().check_if_local_env():
        #     cart_abandonments, last_evaluated_key = Dynamo().query_paginated_all_cart_abandonment(limit=int(10000000))
        #     backoffice_data["backoffice_data_total_cart_abandonment_count"] = str(len(cart_abandonments))
        #     Dynamo().put_entity(backoffice_data)

        html = super().parse_html()
        # cart_abandonments, last_evaluated_key = Dynamo().query_paginated_all_cart_abandonment(limit=int(self.user.user_pagination_count))
        # html.esc("html_pagination", self.show_html_pagination(len(cart_abandonments), backoffice_data["backoffice_data_total_cart_abandonment_count"], "query_paginated_all_cart_abandonment", last_evaluated_key))
        # html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
        # html.esc("showing_total_count_val", len(cart_abandonments))

        # html.esc("html_backoffice_cart_abandonments_table_rows", self.list_html_backoffice_cart_abandonments_table_rows(cart_abandonments))
        return str(html)

    def render_post(self):
        return self.render_get()
