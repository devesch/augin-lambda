from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from utils.AWS.S3 import S3
from utils.utils.Generate import Generate


class PanelGetAwsUploadKeys(BasePage):
    def run(self):
        if self.post.get("create_model"):
            if not self.user:
                return {"error": "no user in request"}
            new_model = ModelController().generate_new_model(self.user, self.post.get("create_model"))
            self.post["key_path"] = new_model["model_upload_path"]

        if self.post.get("key_extension"):
            if not self.post.get("key_path"):
                self.post["key_path"] = ""
            aws_upload_keys = S3().generate_presigned_post(self.post.get("bucket"), self.post["key_path"] + Generate().generate_short_id() + "." + self.post.get("key_extension"))
        elif self.post.get("original_key"):
            aws_upload_keys = S3().generate_presigned_post(self.post.get("bucket"), self.post["original_key"])
        else:
            aws_upload_keys = S3().generate_presigned_post(self.post.get("bucket"), Generate().generate_short_id() + "." + self.post.get("key"))
        aws_upload_keys["fields"]["url"] = aws_upload_keys["url"]
        return {"success": aws_upload_keys["fields"]}
