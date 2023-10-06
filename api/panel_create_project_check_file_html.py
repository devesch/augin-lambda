from python_web_frame.panel_page import PanelPage
from utils.utils.Generate import Generate
from objects.UploadedFile import UploadedFile
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Lambda import Lambda
from utils.Config import lambda_constants


class PanelCreateProjectCheckFileHtml(PanelPage):
    def run(self):
        uploaded_file = Dynamo().get_uploaded_file(self.post["uploaded_file_id"])
        if not uploaded_file["uploaded_file_response"]:
            return {"keep_waiting": "Continue aguardando resposta"}
        check_response = uploaded_file["uploaded_file_response"]
        if "success" in check_response:
            check_response["success"]["message"] = self.translate(check_response["success"]["message"])
            check_response["success"]["file_formats_html"] = self.list_html_uploading_file_formats(check_response["success"]["file_formats"])
        return check_response
