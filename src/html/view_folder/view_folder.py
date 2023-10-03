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
        if self.user and self.path["folder"]["folder_is_accessible"] and not self.path["folder"]["folder_is_password_protected"]:
            return Http().redirect("panel_shared_project/?folder_id=" + self.path["folder"]["folder_id"])

        html = super().parse_html()

        html.esc("html_filter_and_search_section", self.show_html_filter_and_search_section(show_search=False))
        html.esc("folder_id_val", self.path["folder"]["folder_id"])
        html.esc("folder_path_val", self.path["folder"]["folder_path"])
        html.esc("folder_is_accessible_val", self.path["folder"]["folder_is_accessible"])
        html.esc("folder_is_password_protected_val", self.path["folder"]["folder_is_password_protected"])
        return str(html)

    def render_post(self):
        return self.render_get()
