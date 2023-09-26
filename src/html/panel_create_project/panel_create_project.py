from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.model_controller import ModelController
from utils.AWS.Dynamo import Dynamo
from utils.utils.Http import Http
from utils.utils.Date import Date
from utils.Config import lambda_constants
import time


class PanelCreateProject(PanelPage):
    name = "Painel - Criação de Projeto"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        user_plan = self.user.get_user_actual_plan()
        html.esc("plan_maxium_model_size_in_mbs_val", user_plan["plan_maxium_model_size_in_mbs"])
        if user_plan["plan_id"] == lambda_constants["free_plan_id"]:
            html.esc("html_make_an_upgrade_link", self.show_html_make_an_upgrade_link())

        self.check_error_msg(html, self.error_msg)
        already_uploaded_models = ModelController().get_already_uploaded_models(self.user)
        if already_uploaded_models:
            html.esc("html_uploading_models", self.list_html_uploading_models(already_uploaded_models))
            html.esc("uploading_index_input_val", len(already_uploaded_models))
        else:
            html.esc("uploading_index_input_val", 1)
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
            if model["model_state"] == "not_created":
                ModelController().process_model_file_uploaded(model, federated_model)
            else:
                if federated_model:
                    raise Exception("ADD ALREADY EXISTING PROJECT TO FEDERATED PROJECTS")

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
