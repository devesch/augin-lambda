from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from objects.User import load_user
from utils.utils.Validation import Validation
import json


class BackofficeOrdersHtml(BackofficePage):
    def run(self):
        last_evaluated_key = {}
        query_filter = "all"
        if self.post.get("search_user"):
            query = "query_user_orders"
            order_user = load_user(self.post["search_user"])
            if order_user:
                orders = Dynamo().query_user_orders(order_user.user_id)
                return {"success": self.list_html_backoffice_orders_table_rows(orders), "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "query_filter": query_filter, "showing_total_count": len(orders)}
            order = Dynamo().get_order(self.post["search_user"])
            if order:
                orders = [order]
                return {"success": self.list_html_backoffice_orders_table_rows(orders), "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "query_filter": query_filter, "showing_total_count": len(orders)}
            return {"success": "", "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "query_filter": query_filter, "showing_total_count": "0"}
        else:
            if self.post.get("search_order_status") != "all":
                query_filter = self.post["search_order_status"]
                query = "query_paginated_all_orders_from_status"
                orders, last_evaluated_key = Dynamo().query_paginated_all_orders_from_status(self.post["search_order_status"], limit=int(self.user.user_pagination_count))
            else:
                query = "query_paginated_all_orders"
                orders, last_evaluated_key = Dynamo().query_paginated_all_orders(limit=int(self.user.user_pagination_count))
            return {"success": self.list_html_backoffice_orders_table_rows(orders), "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "query_filter": query_filter, "showing_total_count": len(orders)}
