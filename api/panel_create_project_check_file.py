from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.model_controller import ModelController


class PanelCreateProjectCheckFile(PanelPage):
    def run(self):
        raise Exception("TODO")
        check_response = ModelController().check_if_file_uploaded_is_valid(self.post["key"], self.post["original_name"], self.user)
        return {"success": ""}
        if "success" in check_response:
            check_response["success"]["message"] = self.translate(check_response["success"]["message"])
            check_response["success"]["file_formats_html"] = self.list_html_uploading_file_formats(check_response["success"]["file_formats"])
        return check_response
