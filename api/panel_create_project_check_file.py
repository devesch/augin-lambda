from python_web_frame.panel_page import PanelPage
from utils.utils.Generate import Generate
from objects.UploadedFile import UploadedFile
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Lambda import Lambda
from utils.Config import lambda_constants


class PanelCreateProjectCheckFile(PanelPage):
    def run(self):
        uploaded_file = UploadedFile(Generate().generate_short_id(), self.user.user_id, self.post).__dict__
        Dynamo().put_entity(uploaded_file)
        Lambda().invoke(lambda_constants["lambda_check_model_uploaded_file"], "Event", {"uploaded_file_id": uploaded_file["uploaded_file_id"]})
        return {"success": "upload_send_for_check"}
        # check_response = ModelController().check_if_file_uploaded_is_valid(self.post["key"], self.post["original_name"], self.user)
        # if "success" in check_response:
        #     check_response["success"]["message"] = self.translate(check_response["success"]["message"])
        #     check_response["success"]["file_formats_html"] = self.list_html_uploading_file_formats(check_response["success"]["file_formats"])
        # return check_response
