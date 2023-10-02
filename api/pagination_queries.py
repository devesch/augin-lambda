from python_web_frame.panel_page import PanelPage
from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from json import loads
from time import time


class PaginationQueries(BackofficePage, PanelPage):
    def run(self):
        if not self.post.get("query"):
            return {"error": "no command in post"}

        if self.post.get("last_evaluated_key"):
            if self.post.get("last_evaluated_key") == "undefined":
                return {"error": "undefined last_evaluated_key"}
            last_evaluated_key = loads(self.post["last_evaluated_key"])

        if self.post["query"] == "query_paginated_user_orders":
            user_orders = Dynamo().query_paginated_user_orders(self.user.user_id, self.user.user_total_orders_count, self.post["page"])
            return {"success": self.list_html_payment_history_rows(user_orders)}

        return getattr(self, self.post["query"])(last_evaluated_key)

    def query_paginated_all_last_login_users_with_signature(self, last_evaluated_key):
        users, last_evaluated_key = Dynamo().query_paginated_all_last_login_users_with_signature(self.post["query_filter"], last_evaluated_key, limit=int(self.user.user_pagination_count))
        html = self.list_html_backoffice_users_table_rows(users)
        new_itens_count = str(len(users))
        return {"success": html, "last_evaluated_key": last_evaluated_key, "new_itens_count": new_itens_count}

    def query_paginated_all_coupons(self, last_evaluated_key):
        coupons, last_evaluated_key = Dynamo().query_paginated_all_coupons(last_evaluated_key, limit=int(self.user.user_pagination_count))
        html = self.list_html_backoffice_coupons_table_rows(coupons)
        new_itens_count = str(len(coupons))
        return {"success": html, "last_evaluated_key": last_evaluated_key, "new_itens_count": new_itens_count}

    def query_paginated_all_last_login_users(self, last_evaluated_key):
        all_users, last_evaluated_key = Dynamo().query_paginated_all_last_login_users(last_evaluated_key, limit=int(self.user.user_pagination_count))
        html = self.list_html_backoffice_users_table_rows(all_users)
        new_itens_count = str(len(all_users))
        return {"success": html, "last_evaluated_key": last_evaluated_key, "new_itens_count": new_itens_count}

    def query_paginated_all_orders(self, last_evaluated_key):
        orders, last_evaluated_key = Dynamo().query_paginated_all_orders(last_evaluated_key, limit=int(self.user.user_pagination_count))
        html = self.list_html_backoffice_orders_table_rows(orders)
        new_itens_count = str(len(orders))
        return {"success": html, "last_evaluated_key": last_evaluated_key, "new_itens_count": new_itens_count}

    def query_paginated_all_orders_from_status(self, last_evaluated_key):
        if not self.post.get("query_filter"):
            return {"error": "no query_filter in post"}
        if self.post["query_filter"] == "all":
            orders, last_evaluated_key = Dynamo().query_paginated_all_orders(last_evaluated_key, limit=int(self.user.user_pagination_count))
            html = self.list_html_backoffice_orders_table_rows(orders)
            new_itens_count = str(len(orders))
        else:
            orders, last_evaluated_key = Dynamo().query_paginated_all_orders_from_status(self.post["query_filter"], last_evaluated_key, limit=int(self.user.user_pagination_count))
            html = self.list_html_backoffice_orders_table_rows(orders)
            new_itens_count = str(len(orders))
        return {"success": html, "last_evaluated_key": last_evaluated_key, "new_itens_count": new_itens_count}
