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

        return {"success": "model_is_favorite updated"}
