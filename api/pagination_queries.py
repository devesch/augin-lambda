from python_web_frame.backoffice_page import BackofficePage
from python_web_frame.panel_page import PanelPage
from utils.AWS.Dynamo import Dynamo
from json import loads


class PaginationQueries(BackofficePage, PanelPage):
    def run(self):
        if not self.post.get("query"):
            return {"error": "no command in post"}

        if self.post["query"] in ["get_model", "query_user_models_from_state", "query_user_orders"]:
            return {"error": "Esta query não é possível de ser paginada"}

        if self.post.get("last_evaluated_key") and self.post.get("last_evaluated_key") == "undefined":
            return {"error": "undefined last_evaluated_key"}

        last_evaluated_key = loads(self.post["last_evaluated_key"])
        return getattr(self, self.post["query"])(last_evaluated_key)

    def query_paginated_all_cancel_subscriptions(self, last_evaluated_key):
        cancel_subscriptions, last_evaluated_key = Dynamo().query_paginated_all_cancel_subscriptions(last_evaluated_key, limit=int(self.user.user_pagination_count))
        return {"success": self.list_html_backoffice_cancel_subscriptions_table_rows(cancel_subscriptions), "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(cancel_subscriptions))}

    def query_paginated_all_models(self, last_evaluated_key):
        models, last_evaluated_key = Dynamo().query_paginated_all_models(last_evaluated_key, limit=int(self.user.user_pagination_count))
        return {"success": self.list_html_backoffice_models_table_rows(models), "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(models))}

    def query_paginated_all_models_by_filesize_bracket(self, last_evaluated_key):
        models, last_evaluated_key = Dynamo().query_paginated_all_models_by_filesize_bracket(self.post["query_filter"], last_evaluated_key, limit=int(self.user.user_pagination_count))
        return {"success": self.list_html_backoffice_models_table_rows(models), "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(models))}

    def query_paginated_all_models_by_state(self, last_evaluated_key):
        models, last_evaluated_key = Dynamo().query_paginated_all_models_by_state(self.post["query_filter"], last_evaluated_key, limit=int(self.user.user_pagination_count))
        return {"success": self.list_html_backoffice_models_table_rows(models), "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(models))}

    def query_paginated_all_last_login_users_with_signature(self, last_evaluated_key):
        users, last_evaluated_key = Dynamo().query_paginated_all_last_login_users_with_signature(self.post["query_filter"], last_evaluated_key, limit=int(self.user.user_pagination_count))
        return {"success": self.list_html_backoffice_users_table_rows(users), "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(users))}

    def query_paginated_all_coupons(self, last_evaluated_key):
        coupons, last_evaluated_key = Dynamo().query_paginated_all_coupons(last_evaluated_key, limit=int(self.user.user_pagination_count))
        return {"success": self.list_html_backoffice_coupons_table_rows(coupons), "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(coupons))}

    def query_paginated_all_last_login_users(self, last_evaluated_key):
        all_users, last_evaluated_key = Dynamo().query_paginated_all_last_login_users(last_evaluated_key, limit=int(self.user.user_pagination_count))
        return {"success": self.list_html_backoffice_users_table_rows(all_users), "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(all_users))}

    def query_paginated_all_orders(self, last_evaluated_key):
        orders, last_evaluated_key = Dynamo().query_paginated_all_orders(last_evaluated_key, limit=int(self.user.user_pagination_count))
        return {"success": self.list_html_backoffice_orders_table_rows(orders), "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(orders))}

    def query_paginated_all_cart_abandonment(self, last_evaluated_key):
        cart_abandonments, last_evaluated_key = Dynamo().query_paginated_all_cart_abandonment(last_evaluated_key, limit=int(self.user.user_pagination_count))
        return {"success": self.list_html_backoffice_cart_abandonments_table_rows(cart_abandonments), "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(cart_abandonments))}

    def query_paginated_all_recurrence_failure(self, last_evaluated_key):
        recurrence_failures, last_evaluated_key = Dynamo().query_paginated_all_recurrence_failure(last_evaluated_key, limit=int(self.user.user_pagination_count))
        return {"success": self.list_html_backoffice_recurrence_failures_table_rows(recurrence_failures), "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(recurrence_failures))}

    def query_paginated_all_orders_from_status(self, last_evaluated_key):
        if not self.post.get("query_filter"):
            return {"error": "no query_filter in post"}
        if self.post["query_filter"] == "all":
            orders, last_evaluated_key = Dynamo().query_paginated_all_orders(last_evaluated_key, limit=int(self.user.user_pagination_count))
            html = self.list_html_backoffice_orders_table_rows(orders)
        else:
            orders, last_evaluated_key = Dynamo().query_paginated_all_orders_from_status(self.post["query_filter"], last_evaluated_key, limit=int(self.user.user_pagination_count))
            html = self.list_html_backoffice_orders_table_rows(orders)
        return {"success": html, "last_evaluated_key": last_evaluated_key, "new_itens_count": str(len(orders))}
