from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.model_controller import ModelController
from utils.utils.ReadWrite import ReadWrite
from utils.AWS.Dynamo import Dynamo


class PanelExploreProject(PanelPage):
    name = "Painel - Explorar Projetos"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        models_in_processing = Dynamo().query_user_models_from_state(self.user, "in_processing")
        if models_in_processing:
            html.esc("html_models_in_processing", self.list_html_models_in_processing(self.event, models_in_processing))
        html.esc("html_user_folder_rows", self.list_html_user_folder_rows())
        return str(html)

    def render_post(self):
        return self.render_get()
