from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
import json


class BackofficeUsersHtml(BackofficePage):
    def run(self):
        last_evaluated_key = {}
        query_filter = "all"
        if self.post.get("search_user"):
            user = self.load_user(self.post["search_user"])
            if user:
                users = [user.__dict__]
                return {"success": self.list_html_backoffice_users_table_rows(users), "last_evaluated_key": json.dumps(last_evaluated_key), "query": "query_paginated_all_last_login_users", "query_filter": query_filter, "showing_total_count": len(users)}
            else:
                if len(self.post["search_user"]) >= 3:
                    users = Dynamo().query_all_users_first_tree_letters_name(self.post["search_user"].title()[:3])
                    users = self.filter_users_by_name(users)
                else:
                    users = []
                return {"success": self.list_html_backoffice_users_table_rows(users), "last_evaluated_key": json.dumps(last_evaluated_key), "query": "query_all_users_first_tree_letters_name", "query_filter": query_filter, "showing_total_count": len(users)}
        else:
            if self.post.get("search_users_subscription"):
                query = "query_paginated_all_last_login_users_with_signature"
                users, last_evaluated_key = Dynamo().query_paginated_all_last_login_users_with_signature(self.post["search_users_subscription"], limit=int(self.user.user_pagination_count))
            else:
                query = "query_paginated_all_last_login_users"
                users, last_evaluated_key = Dynamo().query_paginated_all_last_login_users(limit=int(self.user.user_pagination_count))
            return {"success": self.list_html_backoffice_users_table_rows(users), "last_evaluated_key": json.dumps(last_evaluated_key), "query": query, "query_filter": query_filter, "showing_total_count": len(users)}

    def filter_users_by_name(self, users):
        filtered_users = []
        if users:
            for user in users:
                if self.post["search_user"].title() in user["user_name"].title():
                    filtered_users.append(user)
        return filtered_users
