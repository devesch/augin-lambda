from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.controllers.project_controller import ProjectController
from utils.AWS.Dynamo import Dynamo
from utils.Config import lambda_constants


class UpdateModel(BasePage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "no command found in post"}

        if self.post.get("model_id"):
            model = Dynamo().get_model(self.post["model_id"])
            if not model["model_user_id"] == self.user.user_id:
                return {"error": "project doesnt belong to user"}

        if self.post["command"] == "create_federated":
            if not self.post.get("federated_required_ids"):
                return {"error": "É necessário selecionar quais arquivos servirão como base do federado."}
            if not self.post.get("federated_name"):
                return {"error": "É necessário informar um nome para o federado."}
            federated_required_ids = self.post["federated_required_ids"].split(",")
            if len(federated_required_ids) <= 1:
                return {"error": "É necessário selecionar no mínimo 2 arquivos que servirão como base do federado."}

            for model_id in federated_required_ids:
                required_model = Dynamo().get_model(model_id)
                if not required_model:
                    return {"error": "Um dos modelos selecionados não existe."}
                if required_model["model_user_id"] != self.user.user_id:
                    return {"error": "Um dos modelos não pertence a este usuário."}

            federated_model = ModelController().generate_new_model(self.user.user_id, filename=self.post["federated_name"].strip(), federated=True, federated_required_ids=federated_required_ids)
            federated_model = ModelController().publish_federated_model(federated_model["model_id"])
            self.user.add_model_to_user_dicts(federated_model)
            return {"success": "create_federated completed"}

        if self.post["command"] == "delete_model":
            ModelController().delete_model(model, self.user)
            return {"success": "model deleted"}

        elif self.post["command"] == "update_model_files":
            selected_model = Dynamo().get_model(self.post["selected_model_id"])
            ModelController().update_model_files(model, selected_model, self.user)
            return {"success": "model files updated"}

        elif self.post["command"] == "update_category":
            if model.get("model_is_federated"):
                model["model_category"] = "federated"
                Dynamo().update_entity(model, "model_category", model["model_category"])
            else:
                if self.post.get("model_category") in lambda_constants["available_categories"]:
                    model["model_category"] = self.post.get("model_category")
                    Dynamo().update_entity(model, "model_category", model["model_category"])
                else:
                    return {"error": "A categoria selecionada é inválida."}
            return {"success": "model category updated"}

        elif self.post["command"] == "update_favorite":
            if self.post["model_is_favorite"] == "True":
                model["model_is_favorite"] = True
            else:
                model["model_is_favorite"] = False
            Dynamo().put_entity(model)
            return {"success": "model favorite updated"}

        elif self.post["command"] == "update_name":
            model["model_name"] = self.post.get("model_name").strip()
            Dynamo().update_entity(model, "model_name", model["model_name"])
            return {"success": "model name updated"}

        elif self.post["command"] == "update_password":
            if self.post.get("model_is_password_protected"):
                if self.post.get("model_is_password_protected") and not self.post.get("model_password"):
                    return {"error": "É necessário informar uma senha."}
            if self.post.get("model_password"):
                model["model_password"] = self.post.get("model_password")
            else:
                model["model_password"] = ""
            model["model_is_password_protected"] = self.post.get("model_is_password_protected")
            Dynamo().put_entity(model)
            return {"success": "model password updated"}

        else:
            return {"error": "no valid command found in post"}
