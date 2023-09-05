import time


class UserFolder:
    def __init__(self, folder_user_email, folder_id, folder_name, folder_path, folder_root_id="") -> None:
        self.pk = "folder#"
        self.sk = "folder_id#" + folder_id
        self.folder_id = folder_id
        self.folder_name = folder_name
        self.folder_user_email = folder_user_email
        self.folder_path = folder_path + "/" + folder_name
        self.folder_root_id = folder_root_id
        self.folder_is_favorite = False
        self.folder_size = "0"
        self.folders = []
        self.files = []
        self.created_at = str(time.time())
        self.entity = "folder"
