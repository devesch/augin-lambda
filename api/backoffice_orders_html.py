from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
import json


class BackofficeOrdersHtml(BackofficePage):
    def run(self):
        last_evaluated_key = {}

        if self.post.get("search_user"):
            query = "query_user_orders"
            order_user = self.load_user(self.post["search_user"])
            if not order_user:
                return {"success": "", "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "showing_total_count": "0"}
            orders = Dynamo().query_user_orders(order_user.user_id)
            return {"success": self.list_html_backoffice_orders_table_rows(orders), "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "showing_total_count": len(orders)}
        else:
            if self.post.get("search_order_status") != "all":
                query = "query_paginated_all_orders_from_status"
                orders, last_evaluated_key = Dynamo().query_paginated_all_orders_from_status(self.post["search_order_status"], limit=int(self.user.user_pagination_count))
            else:
                query = "query_paginated_all_orders"
                orders, last_evaluated_key = Dynamo().query_paginated_all_orders(limit=int(self.user.user_pagination_count))
            return {"success": self.list_html_backoffice_orders_table_rows(orders), "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "showing_total_count": len(orders)}
