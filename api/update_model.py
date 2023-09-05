from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.controllers.project_controller import ProjectController
from utils.AWS.Dynamo import Dynamo
from utils.Config import lambda_constants


class UpdateModel(BasePage):
    def run(self):
        model = Dynamo().get_model_by_id(self.post["model_id"])
        if not model["model_user_email"] == self.user.user_email:
            return {"error": "project doesnt belong to user"}

        if self.post.get("command"):
            if self.post["command"] == "delete_model":
                ModelController().delete_model(model, self.user)

            if self.post["command"] == "update_model_files":
                selected_model = Dynamo().get_model_by_id(self.post["selected_model_id"])
                ModelController().update_model_files(model, selected_model, self.user)

        if self.post.get("model_category"):
            if model.get("model_is_federated"):
                model["model_category"] = "Federated"
                Dynamo().update_entity(model, "model_category", model["model_category"])
            if self.post.get("model_category") in lambda_constants["available_categories"]:
                model["model_category"] = self.post.get("model_category")
                Dynamo().update_entity(model, "model_category", model["model_category"])
            else:
                return {"error": "A categoria selecionada é inválida."}

        if self.post.get("model_is_favorite"):
            if self.post["model_is_favorite"] == "True":
                model["model_is_favorite"] = True
            else:
                model["model_is_favorite"] = False
            Dynamo().put_entity(model)

        if self.post.get("model_name"):
            model["model_name"] = self.post.get("model_name").strip()
            Dynamo().update_entity(model, "model_name", model["model_name"])

        if "model_is_password_protected" in self.post:
            if self.post.get("model_is_password_protected"):
                if self.post.get("model_is_password_protected") and not self.post.get("model_password"):
                    return {"error": "É necessário informar uma senha."}
            if self.post.get("model_password"):
                model["model_password"] = self.post.get("model_password")
            else:
                model["model_password"] = ""
            model["model_is_password_protected"] = self.post.get("model_is_password_protected")
            Dynamo().put_entity(model)

        return {"success": "model updated"}
