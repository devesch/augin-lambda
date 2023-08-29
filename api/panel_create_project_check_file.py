from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.model_controller import ModelController


class PanelCreateProjectCheckFile(PanelPage):
    def run(self):
        return ModelController().check_if_file_uploaded_is_valid(self.post["key"], self.user)
