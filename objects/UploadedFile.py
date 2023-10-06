import time


class UploadedFile:
    def __init__(self, uploaded_file_id, uploaded_file_user_id, uploaded_file_post) -> None:
        self.pk = "uploaded_file#" + uploaded_file_id
        self.sk = "uploaded_file#" + uploaded_file_id
        self.uploaded_file_id = uploaded_file_id
        self.uploaded_file_user_id = uploaded_file_user_id
        self.uploaded_file_post = uploaded_file_post
        self.uploaded_file_response = {}
        self.created_at = str(time.time())
        self.entity = "uploaded_file"
