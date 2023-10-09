from python_web_frame.base_page import BasePage
from objects.AnalyticsAppOpening import AnalyticsAppOpening
from utils.AWS.Dynamo import Dynamo


class appMobile(BasePage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "Nenhum command no post"}

        return getattr(self, self.post["command"])()

    def increase_app_openings(self):
        Dynamo().put_entity(AnalyticsAppOpening().__dict__)
