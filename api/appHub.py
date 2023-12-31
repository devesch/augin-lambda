from python_web_frame.base_page import BasePage
from objects.AnalyticsSoftwareOpening import AnalyticsSoftwareOpening
from utils.AWS.Dynamo import Dynamo


class appHub(BasePage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "Nenhum command no post"}

        return getattr(self, self.post["command"])()

    def increase_software_openings(self):
        Dynamo().put_entity(AnalyticsSoftwareOpening().__dict__)
        return {"success": "Analytics contabilizado"}
