from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from utils.AWS.Dynamo import Dynamo


class ModelDelete(BasePage):
    def run(self):
        model = Dynamo().get_model_by_id(self.post["model_id"])
        if model:
            if model["model_user_email"] == self.user.user_email:
                if model["model_state"] == "completed":
                    user = self.load_user(model["model_user_email"])
                    user.decrease_total_count("user_completed_models_total_count")
                    user.remove_model_from_user_dicts(model)
                ModelController().delete_model(model)
                return {"success": "model deleted"}
        return {"error": "unable to delete model"}
