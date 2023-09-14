from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.model_controller import ModelController
from utils.AWS.Dynamo import Dynamo
from utils.utils.Http import Http
from utils.utils.Date import Date
import time


class PanelCreateProject(PanelPage):
    name = "Painel - Criação de Projeto"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        return str(html)

    def render_post(self):
        models_ids = self.generate_models_ids_from_post()
        if not models_ids:
            return self.render_get_with_error("É necessário fazer o envio dos arquivos")

        federated_model = None
        if self.post.get("create_federated_project_with_processed_files"):
            if not self.post.get("federated_name"):
                return self.render_get_with_error("É necessário informar um nome para o projeto federado")
            federated_model = ModelController().generate_new_model(self.user.user_id, filename=self.post["federated_name"], federated=True, federated_required_ids=models_ids)

        for model_id in models_ids:
            model = Dynamo().get_model(model_id)
            ModelController().process_model_file_uploaded(model, federated_model)

        return Http().redirect("panel_explore_project")

    def generate_models_ids_from_post(self):
        models_ids = []
        if self.post:
            for param, value in self.post.items():
                if "model_id" in param:
                    if not "," in value:
                        models_ids.append(value)
                    else:
                        ids = value.split(",")
                        for id in ids:
                            models_ids.append(id)
        return models_ids
