from python_web_frame.panel_page import PanelPage
from utils.AWS.Dynamo import Dynamo


class PanelCreateProjectUploadingHtml(PanelPage):
    def run(self):
        return {"success": self.show_html_uploading_models(self.post.get("model_filename"), self.post.get("index"))}
