from python_web_frame.panel_page import PanelPage
from utils.AWS.Dynamo import Dynamo


class PanelExploreProjectsModelsInProcessingHtml(PanelPage):
    def run(self):
        if not self.user:
            return {"error": "Nenhum usuário encontrado"}
        models_in_processing = Dynamo().query_user_models_from_state(self.user, "in_processing")
        models_in_processing.extend(Dynamo().query_user_models_from_state(self.user, "error"))
        return {"success": self.list_html_models_in_processing(self.event, models_in_processing)}
