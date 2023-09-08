import time
from utils.AWS.Dynamo import Dynamo
from python_web_frame.controllers.model_controller import ModelController


class UserFolder:
    def __init__(self, folder_user_id, folder_id, folder_name, folder_path, folder_root_id="") -> None:
        self.pk = "folder#" + folder_id
        self.sk = "folder#" + folder_id
        self.folder_id = folder_id
        self.folder_name = folder_name
        self.folder_user_id = folder_user_id
        self.folder_path = folder_path + "/" + folder_name
        self.folder_root_id = folder_root_id
        self.folder_is_favorite = False
        self.folder_size_in_mbs = "0"
        self.folder_foldersize_in_mbs = "0"
        self.folder_filesize_in_mbs = "0"
        self.folders = []
        self.files = []
        self.created_at = str(time.time())
        self.entity = "folder"


def add_folder_to_folder(folder, folder_to_be_added):
    folder["folders"].append(folder_to_be_added["folder_id"])
    folder["folder_foldersize_in_mbs"] = str(int(folder["folder_foldersize_in_mbs"]) + int(folder_to_be_added["folder_size_in_mbs"]))
    folder["folder_size_in_mbs"] = str(int(folder["folder_foldersize_in_mbs"]) + int(folder["folder_filesize_in_mbs"]))

    Dynamo().put_entity(folder)

    folder_to_be_added["folder_root_id"] = folder["folder_id"]
    Dynamo().put_entity(folder_to_be_added)

    if folder["folder_root_id"]:
        update_root_folder_size(folder["folder_root_id"])


def add_file_to_folder(folder, model_id, model_filesize):
    folder["files"].append(model_id)
    folder["folder_filesize_in_mbs"] = str(round(int(folder["folder_filesize_in_mbs"]) + float(ModelController().convert_model_filesize_to_mb(model_filesize))))
    folder["folder_size_in_mbs"] = str(round(int(folder["folder_foldersize_in_mbs"]) + int(folder["folder_filesize_in_mbs"])))
    Dynamo().put_entity(folder)
    if folder["folder_root_id"]:
        update_root_folder_size(folder["folder_root_id"])


def remove_folder_from_folder(folder, folder_to_be_removed):
    folder["folders"].remove(folder_to_be_removed["folder_id"])
    folder["folder_foldersize_in_mbs"] = str(int(folder["folder_foldersize_in_mbs"]) - int(folder_to_be_removed["folder_size_in_mbs"]))
    folder["folder_size_in_mbs"] = str(int(folder["folder_foldersize_in_mbs"]) + int(folder["folder_filesize_in_mbs"]))

    Dynamo().put_entity(folder)

    folder_to_be_removed["folder_root_id"] = ""
    Dynamo().put_entity(folder_to_be_removed)
    if folder["folder_root_id"]:
        update_root_folder_size(folder["folder_root_id"])


def remove_file_from_folder(folder, model_id, model_filesize):
    if model_id in folder["files"]:
        folder["files"].remove(model_id)
        if folder["files"]:
            folder["folder_filesize_in_mbs"] = str(round(int(folder["folder_filesize_in_mbs"]) - float(ModelController().convert_model_filesize_to_mb(model_filesize))))
        else:
            folder["folder_filesize_in_mbs"] = "0"

    folder["folder_size_in_mbs"] = str(int(folder["folder_foldersize_in_mbs"]) + int(folder["folder_filesize_in_mbs"]))
    Dynamo().put_entity(folder)
    if folder["folder_root_id"]:
        update_root_folder_size(folder["folder_root_id"])


def update_root_folder_size(root_id):
    root_folder = Dynamo().get_folder(root_id)

    root_folder["folder_foldersize_in_mbs"] = "0"
    if root_folder["folders"]:
        for folder_id in root_folder["folders"]:
            folder = Dynamo().get_folder(folder_id)
            root_folder["folder_foldersize_in_mbs"] = str(int(root_folder["folder_foldersize_in_mbs"]) + int(folder["folder_size_in_mbs"]))

    root_folder["folder_size_in_mbs"] = str(int(root_folder["folder_foldersize_in_mbs"]) + int(root_folder["folder_filesize_in_mbs"]))
    Dynamo().put_entity(root_folder)
    if root_folder["folder_root_id"]:
        update_root_folder_size(root_folder["folder_root_id"])


def check_if_folder_movement_is_valid(folder, destiny_folder):
    if folder["folder_id"] == destiny_folder["folder_id"]:
        return False

    folder_root_id = destiny_folder["folder_root_id"]
    result = True
    while True:
        if not folder_root_id:
            break

        root_folder = Dynamo().get_folder(folder_root_id)
        if folder["folder_id"] == root_folder["folder_id"]:
            result = False
            break

        folder_root_id = root_folder["folder_root_id"]

    return result
