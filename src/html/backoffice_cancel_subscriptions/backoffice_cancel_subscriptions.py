from python_web_frame.backoffice_page import BackofficePage
from objects.BackofficeData import get_backoffice_data
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
import json


class BackofficeCancelSubscriptions(BackofficePage):
    name = "Backoffice - Assinaturas canceladas"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        backoffice_data = get_backoffice_data()

        if Validation().check_if_local_env():
            cancel_subscriptions, last_evaluated_key = Dynamo().query_paginated_all_cancel_subscriptions(limit=int(10000000))
            backoffice_data["backoffice_data_total_cancel_subscription_count"] = str(len(cancel_subscriptions))
            Dynamo().put_entity(backoffice_data)

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        cancel_subscriptions, last_evaluated_key = Dynamo().query_paginated_all_cancel_subscriptions(limit=int(self.user.user_pagination_count))
        html.esc("html_pagination", self.show_html_pagination(len(cancel_subscriptions), backoffice_data["backoffice_data_total_cancel_subscription_count"], "query_paginated_all_cancel_subscriptions", last_evaluated_key))
        html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
        html.esc("showing_total_count_val", len(cancel_subscriptions))

        html.esc("html_backoffice_cancel_subscriptions_table_rows", self.list_html_backoffice_cancel_subscriptions_table_rows(cancel_subscriptions))
        return str(html)

    def render_post(self):
        return self.render_get()
