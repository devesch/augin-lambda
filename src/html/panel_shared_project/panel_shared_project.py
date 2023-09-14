from python_web_frame.panel_page import PanelPage
from utils.utils.ReadWrite import ReadWrite
from utils.AWS.Dynamo import Dynamo
from utils.Config import lambda_constants


class PanelSharedProject(PanelPage):
    name = "Painel - Compartilhados Projetos"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        html.esc("html_project_filter_options", self.list_html_project_filter_options())
        html.esc("html_user_folder_rows", self.list_html_user_folder_rows())
        return str(html)

    def render_post(self):
        return self.render_get()

    def list_html_project_filter_options(self):
        full_html = []
        for category_id, category in lambda_constants["available_categories"].items():
            html = ReadWrite().read_html("panel_explore_project/_codes/html_project_filter_option")
            html.esc("category_val", category_id)
            html.esc("category_name_val", self.translate(category["category_name"]))
            full_html.append(str(html))

        html = ReadWrite().read_html("panel_explore_project/_codes/html_project_filter_option")
        html.esc("category_val", "favorite")
        html.esc("category_name_val", self.translate("Favoritos"))
        full_html.append(str(html))
        html = ReadWrite().read_html("panel_explore_project/_codes/html_project_filter_option")
        html.esc("category_val", "not_federated")
        html.esc("category_name_val", self.translate("Não Federados"))
        full_html.append(str(html))
        return "".join(full_html)
