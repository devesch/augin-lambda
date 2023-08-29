from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.model_controller import ModelController
from utils.AWS.Dynamo import Dynamo
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
        models_ids = self.generate_models_ids_from_post()
        if not models_ids:
            return self.render_get_with_error("É necessário fazer o envio dos arquivos")

        for model_id in models_ids:
            model = Dynamo().get_model_by_id(model_id)
            ModelController().process_model_file_uploaded(model)

        return Http().redirect("panel_explore_project")

    def generate_models_ids_from_post(self):
        models_ids = []
        if self.post:
            for param, value in self.post.items():
                if "model_id" in param:
                    models_ids.append(value)
        return models_ids
