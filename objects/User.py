import time
from uuid import uuid4
from utils.AWS.Dynamo import Dynamo
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.Generate import Generate
from objects.UserPassword import UserPassword
from objects.UserAuthToken import UserAuthToken


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

    def add_model_to_user_dicts(self, model):
        self.user_dicts["files"].append(model["model_id"])
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
