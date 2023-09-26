from python_web_frame.panel_page import PanelPage
from utils.utils.ReadWrite import ReadWrite
from utils.AWS.Dynamo import Dynamo
from utils.Config import lambda_constants


class PanelExploreProject(PanelPage):
    name = "Painel - Explorar Projetos"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        # self.user.user_dicts = {"folders": [], "files": []}
        # Dynamo().put_entity(self.user.__dict__)

        html = super().parse_html()
        user_plan = self.user.get_user_actual_plan()
        if user_plan["plan_maxium_federated_size_in_mbs"] != "0":
            html.esc("html_create_federated_button", self.show_html_create_federated_button())

        html.esc("html_project_filter_options", self.list_html_project_filter_options())
        models_in_processing = Dynamo().query_user_models_from_state(self.user, "in_processing")
        if models_in_processing:
            html.esc("html_models_in_processing", self.list_html_models_in_processing(self.event, models_in_processing))
        else:
            html.esc("models_in_processing_visibility_val", "display:none;")
        html.esc("html_user_folder_rows", self.list_html_user_folder_rows(user_plan))
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
