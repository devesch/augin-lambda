from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.controllers.project_controller import ProjectController
from utils.AWS.Dynamo import Dynamo


class UpdateModel(BasePage):
    def run(self):
        model = Dynamo().get_model_by_id(self.post["model_id"])
        if not model["model_user_email"] == self.user.user_email:
            return {"error": "project doesnt belong to user"}

        if self.post.get("model_is_favorite"):
            if self.post["model_is_favorite"] == "True":
                model["model_is_favorite"] = True
            else:
                model["model_is_favorite"] = False
            Dynamo().put_entity(model)

        if self.post.get("model_filename"):
            model["model_filename"] = self.post.get("model_filename").strip()
            Dynamo().update_entity(model, "model_filename", model["model_filename"])

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
