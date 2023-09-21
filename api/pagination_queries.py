from python_web_frame.panel_page import PanelPage
from utils.AWS.Dynamo import Dynamo
from json import loads
from time import time


class PaginationQueries(PanelPage):
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

        # if self.post["query"] == "query_paginated_all_last_login_users":
        #     users, last_evaluated_key = self.dynamo.query_paginated_all_last_login_users(last_evaluated_key, limit=int(self.user.user_pagination_count))
        #     html = self.list_html_backoffice_users_table_rows(users)
        #     new_itens_count = str(len(users))

        # return {"success": html, "last_evaluated_key": last_evaluated_key, "new_itens_count": new_itens_count}
