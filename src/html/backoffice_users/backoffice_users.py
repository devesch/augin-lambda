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
        if not self.post.get("search_by_name"):
            if not self.post.get("user_email"):
                return self.render_get_with_error("É necessário informar um email de usuário.")

        if self.post.get("add_credits"):
            return self.utils.redirect("backoffice_user_add_credits/?user_encoded_email=" + self.utils.encode_to_b64(self.post["user_email"]))
        if self.post.get("user_orders"):
            return self.utils.redirect("panel_order_history/?user_encoded_email=" + self.utils.encode_to_b64(self.post["user_email"]))
        if self.post.get("user_projects"):
            return self.utils.redirect("panel_projects/?projects_display=pending&user_encoded_email=" + self.utils.encode_to_b64(self.post["user_email"]))
        if self.post.get("user_login_as"):
            user_login_as = self.load_user(self.post["user_email"])
            return {"html": self.utils.redirect("panel_projects/?projects_display=pending"), "command": "login", "user_auth_token": user_login_as.user_auth_token}
        return self.render_get()
