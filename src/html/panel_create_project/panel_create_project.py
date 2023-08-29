from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.model_controller import ModelController
from utils.utils.Http import Http


class PanelCreateProject(PanelPage):
    name = "Painel - Criação de Projeto"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        check_file = ModelController().check_if_file_uploaded_is_valid(self.post.get("uploaded_file"))
        if "error" in check_file:
            return self.render_get_with_error(check_file["error"])

        process_file = ModelController().process_model_file_uploaded(check_file["model"], check_file["file_format"])
        return Http().redirect("panel_explore_project")
