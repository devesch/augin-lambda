from python_web_frame.backoffice_page import BackofficePage
from utils.utils.Validation import Validation
from utils.AWS.Dynamo import Dynamo
import json


class BackofficeUsers(BackofficePage):
    name = "Backoffice - Usuários"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        backoffice_data = self.get_backoffice_data()

        if Validation().check_if_local_env():
            users, last_evaluated_key = Dynamo().query_paginated_all_last_login_users(limit=int(10000000))
            backoffice_data["backoffice_data_total_user_count"] = str(len(users))
            Dynamo().put_entity(backoffice_data)

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)

        users, last_evaluated_key = Dynamo().query_paginated_all_last_login_users(limit=int(self.user.user_pagination_count))
        html.esc("html_pagination", self.show_html_pagination(len(users), backoffice_data["backoffice_data_total_user_count"], "query_paginated_all_last_login_users", last_evaluated_key, self.path.get("user_has_subscription", "")))
        html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
        html.esc("showing_total_count_val", len(users))

        html.esc("html_backoffice_users_table_rows", self.list_html_backoffice_users_table_rows(users))
        return str(html)

    def render_post(self):
        return self.render_get()
