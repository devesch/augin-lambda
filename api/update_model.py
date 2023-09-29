from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.controllers.project_controller import ProjectController
from utils.AWS.Dynamo import Dynamo
from utils.Config import lambda_constants
from objects.UserFolder import update_root_folder_size


class UpdateModel(BasePage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "Nenhum command no post"}

        model = None
        if self.post.get("model_id"):
            model = Dynamo().get_model(self.post["model_id"])
            if model["model_user_id"] != self.user.user_id and self.user.user_crendential != "admin":
                return {"error": "Este model_id não pertence ao usuário"}

        return getattr(self, self.post["command"])(model)

    def remove_model_id_from_federated_model(self, model):
        ModelController().remove_model_id_from_federated_model(model, self.post["model_id_to_be_removed"])
        if model["model_folder_id"]:
            update_root_folder_size(model["model_folder_id"])
        return {"success": "Federado atualizado"}

    def update_federated_model_required_ids(self, model):
        if not self.post.get("federated_required_ids"):
            return {"error": "É necessário selecionar algum projeto para compor o federado"}
        federated_required_models_ids = self.post["federated_required_ids"].split(",")
        federated_required_models = Dynamo().batch_get_models(federated_required_models_ids)
        if not federated_required_models:
            return {"error": "Nenhum modelo selecionado encontrado"}
        for required_model in federated_required_models:
            if required_model["model_format"] != "ifc":
                return {"error": "Um dos modelos selecionados não é do tipo IFC"}
            if required_model["model_state"] != "completed":
                return {"error": "Um dos modelos selecionados não foi processado"}
            if required_model["model_user_id"] != self.user.user_id:
                return {"error": "Um dos modelos selecionados não pertence a este usuário"}

        ModelController().update_federated_required_models(model, federated_required_models)
        if model["model_folder_id"]:
            update_root_folder_size(model["model_folder_id"])

        return {"success": "Federado atualizado", "federated_required_ids": ",".join(federated_required_models_ids)}

    def create_federated(self, model):
        if not self.post.get("federated_required_ids"):
            return {"error": "É necessário selecionar quais arquivos servirão como base do federado"}
        if not self.post.get("federated_name"):
            return {"error": "É necessário informar um nome para o federado"}
        federated_required_ids = self.post["federated_required_ids"].split(",")
        if len(federated_required_ids) <= 1:
            return {"error": "É necessário selecionar no mínimo 2 arquivos que servirão como base do federado"}

        for model_id in federated_required_ids:
            required_model = Dynamo().get_model(model_id)
            if not required_model:
                return {"error": "Um dos modelos selecionados não existe"}
            if required_model["model_user_id"] != self.user.user_id:
                return {"error": "Um dos modelos não pertence a este usuário"}

        federated_model = ModelController().generate_new_model(self.user, filename=self.post["federated_name"].strip(), federated=True, federated_required_ids=federated_required_ids)
        federated_model = ModelController().publish_federated_model(federated_model["model_id"])
        self.user.add_model_to_user_dicts(federated_model)
        return {"success": "create_federated completed"}

    def delete_model(self, model):
        ModelController().delete_model(model, self.user)
        return {"success": "model deleted"}

    def update_model_files(self, model):
        selected_model = Dynamo().get_model(self.post["selected_model_id"])
        if not selected_model:
            return {"error": "O projeto selecionado é inválido"}
        if model["model_id"] == selected_model["model_id"]:
            return {"error": "É necessário escolher um arquivo diferente do original para a substitução"}
        if (model["model_format"] == "ifc" and selected_model["model_format"] != "ifc") and (model["model_format"] in ["fbx", "glb"] and selected_model["model_format"] == "ifc"):
            return {"error": "É necessário escolher um arquivo do mesmo formato para a substitução"}
        ModelController().update_model_files(model, selected_model, self.user)
        return {"success": "model files updated"}

    def update_category(self, model):
        if model["model_is_federated"]:
            model["model_category"] = "federated"
            Dynamo().update_entity(model, "model_category", model["model_category"])
        else:
            if self.post.get("model_category") in lambda_constants["available_categories"]:
                model["model_category"] = self.post.get("model_category")
                Dynamo().update_entity(model, "model_category", model["model_category"])
            else:
                return {"error": "A categoria selecionada é inválida"}
        return {"success": "model category updated"}

    def update_name(self, model):
        model["model_name"] = self.post.get("model_name").strip()
        Dynamo().update_entity(model, "model_name", model["model_name"])
        return {"success": "model name updated"}

    def update_password(self, model):
        model_is_accessible = self.post.get("model_is_accessible")
        model_is_password_protected = self.post.get("model_is_password_protected")
        model_password = self.post.get("model_password")

        model["model_is_accessible"] = model_is_accessible
        if model_is_accessible and model_is_password_protected and not model_password:
            return {"error": "É necessário informar uma senha"}
        model["model_password"] = model_password if model_password else ""
        model["model_is_password_protected"] = model_is_password_protected

        Dynamo().put_entity(model)
        return {"success": "model password updated"}
