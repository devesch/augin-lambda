from python_web_frame.backoffice_page import BackofficePage
from objects.BackofficeData import get_backoffice_data
from utils.utils.Validation import Validation
from utils.AWS.Dynamo import Dynamo
import json


class BackofficeUsers(BackofficePage):
    name = "Backoffice - Usuários"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        backoffice_data = get_backoffice_data()

        if Validation().check_if_local_env():
            from objects.User import load_user
            from python_web_frame.controllers.model_controller import ModelController

            users, last_evaluated_key = Dynamo().query_paginated_all_last_login_users(limit=int(10000000))
            backoffice_data["backoffice_data_total_user_count"] = str(len(users))
            Dynamo().put_entity(backoffice_data)

            # for user in users:
            #     user = load_user(user["user_id"])
            #     user.user_used_cloud_space_in_mbs = "0.0"
            #     all_user_models = []
            #     all_user_models.extend(Dynamo().query_user_models_from_state(user, "not_created", limit=100000))
            #     all_user_models.extend(Dynamo().query_user_models_from_state(user, "in_processing", limit=100000))
            #     all_user_models.extend(Dynamo().query_user_models_from_state(user, "completed", limit=100000))

            #     models_total_size = 0
            #     for model in all_user_models:
            #         if not model["model_is_federated"]:
            #             models_total_size += float(ModelController().convert_model_filesize_to_mb(model["model_filesize"]))
            #     user.increase_used_cloud_space_in_mbs(models_total_size)

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
