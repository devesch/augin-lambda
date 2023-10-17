from python_web_frame.backoffice_page import BackofficePage
from objects.BackofficeData import get_backoffice_data
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
import json


class BackofficeRecurrenceFailures(BackofficePage):
    name = "Backoffice - Falhas de recorrência"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        backoffice_data = get_backoffice_data()

        if Validation().check_if_local_env():
            recurrence_failures, last_evaluated_key = Dynamo().query_paginated_all_recurrence_failure(limit=int(10000000))
            backoffice_data["backoffice_data_total_recorrence_failure_count"] = str(len(recurrence_failures))
            Dynamo().put_entity(backoffice_data)

        html = super().parse_html()
        recurrence_failures, last_evaluated_key = Dynamo().query_paginated_all_recurrence_failure(limit=int(self.user.user_pagination_count))
        html.esc("html_pagination", self.show_html_pagination(len(recurrence_failures), backoffice_data["backoffice_data_total_recorrence_failure_count"], "query_paginated_all_recurrence_failure", last_evaluated_key))
        html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
        html.esc("showing_total_count_val", len(recurrence_failures))

        html.esc("html_backoffice_recurrence_failures_table_rows", self.list_html_backoffice_recurrence_failures_table_rows(recurrence_failures))
        return str(html)

    def render_post(self):
        return self.render_get()
