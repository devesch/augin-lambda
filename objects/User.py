import time
from uuid import uuid4
from utils.AWS.Dynamo import Dynamo
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.Generate import Generate
from objects.UserPassword import UserPassword
from objects.UserAuthToken import UserAuthToken
from objects.UserFolder import UserFolder
from utils.utils.Sort import Sort


class User:
    def __init__(self, user_email="") -> None:
        self.pk = "user#" + user_email
        self.sk = "user#" + user_email
        self.user_email = user_email
        self.user_id = str(time.time())

        self.user_name = ""
        self.user_first_three_letters_name = ""
        self.user_password = ""
        self.user_status = "not_created"
        self.user_phone = ""
        self.user_address_data = {"user_country": "BR", "user_zip_code": "", "user_state": "", "user_city": "", "user_city_code": "", "user_street": "", "user_neighborhood": "", "user_street_number": "", "user_complement": ""}
        self.user_client_type = "physical"  # physical / company / international
        self.user_credential = ""
        self.user_ip = ""
        self.user_cart_currency = ""
        self.user_dicts = {"folders": [], "files": []}

        # self.user_completed_models_total_count = "0"
        # self.user_model_datalist_builder = []
        # self.user_model_datalist_work = []
        # self.user_model_datalist_city_region = []
        # self.user_model_datalist_category = []

        self.user_last_login_at = str(time.time())
        self.created_at = str(time.time())
        self.entity = "user"

    def move_model_to_another_folder(self, model, new_folder=""):
        if model.get("model_folder_id"):
            model_folder = Dynamo().get_folder(model["model_folder_id"])
            model_folder["files"].remove(model["model_id"])
            Dynamo().put_entity(model_folder)
        else:
            self.user_dicts["files"].remove(model["model_id"])

        if new_folder:
            model["model_folder_id"] = new_folder["folder_id"]
            new_folder["files"].append(model["model_id"])
            Dynamo().put_entity(new_folder)
        else:
            model["model_folder_id"] = ""
            self.user_dicts["files"].append(model["model_id"])

        Dynamo().put_entity(self.__dict__)
        Dynamo().put_entity(model)

    def generate_folder_data(self, folder_id=None):

        user_folder_is_user = False
        if not folder_id:
            user_folder = self.user_dicts
            user_folder_is_user = True
        else:
            user_folder = Dynamo().get_folder(folder_id)

        folder_folders = []
        folder_files = []

        deleted_folders = []
        deleted_files = []

        if user_folder["folders"]:
            for folder_id in user_folder["folders"]:
                folder = Dynamo().get_folder(folder_id)
                if folder:
                    folder_folders.append(folder)
                else:
                    if folder_id not in deleted_folders:
                        deleted_folders.append(folder_id)

        if user_folder["files"]:
            for model_id in user_folder["files"]:
                model = Dynamo().get_model_by_id(model_id)
                if model:
                    folder_files.append(model)
                else:
                    if model_id not in deleted_files:
                        deleted_files.append(model_id)

        if deleted_folders:
            for folder_id in deleted_folders:
                user_folder["folders"].remove(folder_id)

        if deleted_files:
            for model_id in deleted_files:
                user_folder["files"].remove(model_id)

        if deleted_files or deleted_folders:
            if user_folder_is_user:
                Dynamo().put_entity(self.__dict__)
            else:
                Dynamo().put_entity(user_folder)

        user_folder["folders"] = folder_folders
        user_folder["files"] = folder_files

        return user_folder

    def create_new_folder(self, new_folder_name, root_folder_id=""):
        if not root_folder_id:
            root_folder_id = ""
            new_folder = UserFolder(self.user_email, Generate().generate_short_id(), new_folder_name, "").__dict__
            Dynamo().put_entity(new_folder)
            self.user_dicts["folders"].append(new_folder["folder_id"])
            Dynamo().put_entity(self.__dict__)
        else:
            root_folder = Dynamo().get_folder(root_folder_id)
            new_folder = UserFolder(self.user_email, Generate().generate_short_id(), new_folder_name, root_folder["folder_path"], root_folder["folder_id"]).__dict__
            Dynamo().put_entity(new_folder)
            root_folder["folders"].append(new_folder["folder_id"])
            Dynamo().put_entity(root_folder)

    def delete_folder(self, folder):
        if folder["folder_id"] in self.user_dicts["folders"]:
            self.user_dicts["folders"].remove(folder["folder_id"])
            Dynamo().put_entity(self.__dict__)
        else:
            root_folder = Dynamo().get_folder(folder["folder_root_id"])
            root_folder["folders"].remove(folder["folder_id"])
            Dynamo().put_entity(root_folder)
        Dynamo().delete_entity(folder)

    # def rename_folder(self, folder_new_name, folder_path=None):
    #     user_folder = self.find_folder(folder_path)

    #     if folder_new_name in user_folder["folders"]:
    #         return False

    #     folders_names = folder_path.split("/")
    #     if len(folders_names) >= 2:
    #         root_user_folder = self.find_folder(folder_path.split("/")[-2])
    #     else:
    #         root_user_folder = self.find_folder()

    #     root_user_folder["folders"][folder_new_name] = root_user_folder["folders"][folder_path.split("/")[-1]]
    #     root_user_folder["folders"][folder_new_name]["folder_name"] = folder_new_name
    #     del root_user_folder["folders"][folder_path.split("/")[-1]]

    #     Dynamo().put_entity(self.__dict__)
    #     return True

    def add_model_to_user_dicts(self, model):
        self.user_dicts["files"].append(model["model_id"])
        Dynamo().put_entity(self.__dict__)

    def remove_model_from_user_dicts(self, model):
        raise Exception("TODO")
        if model["model_id"] in self.user_dicts["files"]:
            self.user_dicts["files"].remove(model["model_id"])
        Dynamo().put_entity(self.__dict__)

    def increase_total_count(self, param):
        current_value = int(getattr(self, param))
        new_value = current_value + 1
        setattr(self, param, str(new_value))
        Dynamo().update_entity(self.__dict__, param, str(new_value))

    def decrease_total_count(self, param):
        current_value = int(getattr(self, param))
        new_value = current_value - 1
        setattr(self, param, str(new_value))
        Dynamo().update_entity(self.__dict__, param, str(new_value))

    def update_last_login_at(self):
        if int(float(self.user_last_login_at)) + 3000 < int(time()):
            self.user_last_login_at = str(time())
            Dynamo().update_entity(self.__dict__, "user_last_login_at", self.user_last_login_at)

    def update_cart_currency(self):
        if self.user_address_data["user_country"] == "BR":
            self.user_cart_currency = "brl"
        elif self.user_address_data["user_country"] != "BR":
            self.user_cart_currency = "usd"

    def load_information(self):
        if not self.user_email:
            return
        user_data = Dynamo().get_user(self.user_email)
        if user_data:
            for attribute in user_data:
                setattr(self, attribute, user_data[attribute])
        self.update_cart_currency()

    def load_information_with_auth_token(self, user_auth_token):
        if not user_auth_token:
            return
        if user_auth_token:
            auth_token_item = Dynamo().get_auth_token(user_auth_token)
            if auth_token_item:
                self.user_email = auth_token_item["auth_user_email"]
        self.load_information()
        self.user_auth_token = user_auth_token

    def update_auth_token(self):
        self.user_last_login_at = str(time.time())
        self.user_auth_token = str(uuid4())
        auth_token = UserAuthToken(self.user_auth_token, self.user_email)
        Dynamo().put_entity(self.__dict__)
        Dynamo().put_entity(auth_token.__dict__)

    def check_if_password_is_corrected(self, user_password):
        password_item = Dynamo().get_entity_from_crypto({"pk": "user#" + self.user_email, "sk": "pass#" + self.user_email})
        if password_item:
            if "Item" in password_item:
                if "user_password" in password_item["Item"]:
                    if EncodeDecode().encode_to_project_password(user_password, password_item["Item"]["user_salt"]) == password_item["Item"]["user_password"]:
                        return True
        return False

    def update_password(self, user_password, user_salt):
        password_item = UserPassword(self.user_email, EncodeDecode().encode_to_project_password(user_password, user_salt), user_salt)
        Dynamo().put_entity_into_crypto(password_item.__dict__)


def sort_user_folders(user_folders, sort_attribute="folder_name", sort_reverse=False):
    sort_reverse = sort_reverse == "True"
    sort_reverse = not sort_reverse

    if not sort_attribute:
        sort_attribute = "folder_name"
    if sort_attribute == "model_name":
        sort_attribute = "folder_name"
    if sort_attribute == "model_filesize_ifc":
        sort_attribute = "folder_size"

    favorited_folders = []
    normal_folders = []
    sorted_folders = []
    if user_folders:
        for folder in user_folders:
            if folder.get("folder_is_favorite"):
                sorted_folders.append(folder)
            else:
                normal_folders.append(folder)

    if sort_attribute == "folder_name":
        sort_reverse = not sort_reverse
    if sort_attribute == "folder_name":
        favorited_folders = Sort().sort_dict_list(favorited_folders, sort_attribute, reverse=sort_reverse, integer=False)
        normal_folders = Sort().sort_dict_list(normal_folders, sort_attribute, reverse=sort_reverse, integer=False)
    else:
        favorited_folders = Sort().sort_dict_list(favorited_folders, sort_attribute, reverse=sort_reverse, integer=True)
        normal_folders = Sort().sort_dict_list(normal_folders, sort_attribute, reverse=sort_reverse, integer=True)

    sorted_folders.extend(favorited_folders)
    sorted_folders.extend(normal_folders)
    return sorted_folders
