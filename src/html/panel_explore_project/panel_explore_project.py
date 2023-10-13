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
        html = super().parse_html()

        user_plan = self.user.get_user_actual_plan()

        html.esc("html_filter_and_search_section", self.show_html_filter_and_search_section())
        if user_plan["plan_maxium_federated_size_in_mbs"] != "0":
            html.esc("html_create_federated_button", self.show_html_create_federated_button())
        else:
            html.esc("html_create_federated_button", ReadWrite().read_html("panel_explore_project/_codes/html_create_federated_button_blocked"))

        html.esc("html_upgrade_button", self.show_html_upgrade_button(user_plan))
        models_in_processing = Dynamo().query_user_models_from_state(self.user, "in_processing")
        models_with_error = Dynamo().query_user_models_from_state(self.user, "error")

        models_in_processing.extend(models_with_error)
        if models_in_processing:
            html.esc("html_models_in_processing", self.list_html_models_in_processing(self.event, models_in_processing))
        else:
            html.esc("models_in_processing_visibility_val", "display:none;")
        html.esc("html_user_folder_rows", self.list_html_user_folder_rows(user_plan))
        return str(html)

    def render_post(self):
        return self.render_get()
