from python_web_frame.backoffice_page import BackofficePage


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
        return str(html)

    def render_post(self):
        return self.render_get()
