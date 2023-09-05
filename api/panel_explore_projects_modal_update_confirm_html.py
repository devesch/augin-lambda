from python_web_frame.panel_page import PanelPage
from utils.AWS.Dynamo import Dynamo


class PanelExploreProjectsModalUpdateConfirmHtml(PanelPage):
    def run(self):
        original_model = Dynamo().get_model_by_id(self.post["original_model_id"])
        new_model = Dynamo().get_model_by_id(self.post["new_model_id"])
        return {"success": self.show_html_update_modal_update_confirm(original_model, new_model)}
