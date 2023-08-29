from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.model_controller import ModelController
from utils.AWS.Dynamo import Dynamo
from utils.utils.Sort import Sort
from utils.utils.ReadWrite import ReadWrite


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
        return str(html)

    def render_post(self):
        return self.render_get()

    def list_html_models_in_processing(self, event, models_in_processing):
        full_html = []
        if models_in_processing:
            models_in_processing = Sort().sort_dict_list(models_in_processing, "created_at", reverse=True, integer=True)
            for model in models_in_processing:
                if ModelController().check_if_model_in_processing_is_with_error(model["created_at"]):
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_models_in_processing_with_error")
                else:
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_models_in_processing")
                if "dev" in event.get_prefix():
                    html.esc("model_was_processed_where_val", model["model_was_processed_where"])
                html.esc("model_id_val", model["model_id"])
                html.esc("model_filename_val", model["model_filename"])
                html.esc("model_processing_percentage_val", model["model_processing_percentage"])
                full_html.append(str(html))
        return "".join(full_html)
