from python_web_frame.backoffice_page import BackofficePage
from utils.Config import lambda_constants
from utils.utils.ReadWrite import ReadWrite


class BackofficeCreatePlan(BackofficePage):
    name = "Backoffice - Criar Plano"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()

        if self.post:
            if self.post.get("plan_available_annually"):
                html.esc("plan_available_annually_checked_val", "checked='checked'")
            else:
                html.esc("annually_div_visibility_val", "display:none;")

            if self.post.get("plan_available_monthly"):
                html.esc("plan_available_monthly_checked_val", "checked='checked'")
            else:
                html.esc("monthly_div_visibility_val", "display:none;")
        else:
            html.esc("plan_available_annually_checked_val", "checked='checked'")
            html.esc("plan_available_monthly_checked_val", "checked='checked'")

        html.esc("html_plan_reference_tracker_options", self.list_html_plan_reference_tracker_options())
        return str(html)

    def render_post(self):
        return self.render_get()

    def list_html_plan_reference_tracker_options(self):
        full_html = []
        for plan_reference_tracker in lambda_constants["plan_reference_trackers"]:
            html = ReadWrite().read_html("backoffice_create_plan/_codes/html_plan_reference_tracker_options")
            html.esc("plan_reference_tracker_val", plan_reference_tracker)
            html.esc("plan_reference_tracker_name_val", self.translate(plan_reference_tracker))
            if self.post.get("plan_reference_tracker") == plan_reference_tracker:
                html.esc("pre_sel_val", "selected='selected'")
            full_html.append(str(html))
        return "".join(full_html)
