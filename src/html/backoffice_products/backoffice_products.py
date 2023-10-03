from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
import json


class BackofficeProducts(BackofficePage):
    name = "Backoffice - Produtos"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        backoffice_data = self.get_backoffice_data()

        if Validation().check_if_local_env():
            products, last_evaluated_key = Dynamo().query_paginated_all_products(limit=int(10000000))
            backoffice_data["backoffice_data_total_product_count"] = str(len(products))
            Dynamo().put_entity(backoffice_data)

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        products, last_evaluated_key = Dynamo().query_paginated_all_products(limit=int(self.user.user_pagination_count))
        html.esc("html_pagination", self.show_html_pagination(len(products), backoffice_data["backoffice_data_total_product_count"], "query_paginated_all_products", last_evaluated_key))
        html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
        html.esc("showing_total_count_val", len(products))

        html.esc("html_backoffice_products_table_rows", self.list_html_backoffice_products_table_rows(products))
        return str(html)

    def render_post(self):
        return self.render_get()
