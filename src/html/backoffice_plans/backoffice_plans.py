from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo


class BackofficePlans(BackofficePage):
    name = "Backoffice - Planos"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()

        plans = Dynamo().query_entity("plan")
        html.esc("html_backoffice_plans_table_rows", self.list_html_backoffice_plans_table_rows(plans))
        return str(html)

    def render_post(self):
        return self.render_get()
