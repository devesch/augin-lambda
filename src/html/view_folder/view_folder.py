from python_web_frame.panel_page import PanelPage
from utils.utils.Http import Http


class ViewFolder(PanelPage):
    name = "Visualizar Pasta"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        if not self.path.get("folder"):
            return Http().redirect("user_login")

        if self.user:
            return Http().redirect("panel_shared_project/?folder_id=" + self.path["folder"]["folder_id"])

        html = super().parse_html()
        html.esc("html_project_filter_options", self.list_html_project_filter_options())
        html.esc("folder_id_val", self.path["folder"]["folder_id"])
        return str(html)

    def render_post(self):
        return self.render_get()
