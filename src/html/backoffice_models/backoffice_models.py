from python_web_frame.backoffice_page import BackofficePage
from python_web_frame.controllers.model_controller import ModelController
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
from objects.BackofficeData import get_backoffice_data
import json


class BackofficeModels(BackofficePage):
    name = "Backoffice - Modelos"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        backoffice_data = get_backoffice_data()

        if Validation().check_if_local_env():
            models, last_evaluated_key = Dynamo().query_paginated_all_models(limit=int(10000000))
            backoffice_data["backoffice_data_total_model_count"] = str(len(models))
            Dynamo().put_entity(backoffice_data)
            if models:
                for model in models:
                    if not "model_visualization_count" in model:
                        model["model_visualization_count"] = "0"
                    if not "model_error_msg" in model:
                        model["model_error_msg"] = ""
                    if not "model_processing_started_at" in model:
                        model["model_processing_started_at"] = model["created_at"]
                    Dynamo().put_entity(model)

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        models, last_evaluated_key = Dynamo().query_paginated_all_models(limit=int(self.user.user_pagination_count))
        html.esc("html_pagination", self.show_html_pagination(len(models), backoffice_data["backoffice_data_total_model_count"], "query_paginated_all_models", last_evaluated_key))
        html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
        html.esc("showing_total_count_val", len(models))

        html.esc("html_backoffice_models_table_rows", self.list_html_backoffice_models_table_rows(models))
        return str(html)

    def render_post(self):
        return self.render_get()
