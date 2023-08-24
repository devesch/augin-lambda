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
        self.user_name = ""
        self.user_last_name = ""
        self.user_tqs_id = ""
        self.user_password = ""
        self.user_completed_models_total_count = "0"
        self.user_model_datalist_builder = []
        self.user_model_datalist_work = []
        self.user_model_datalist_city_region = []
        self.user_model_datalist_category = []
        self.user_status = "not_created"
        self.user_credential = ""
        self.user_last_login_at = str(time.time())
        self.user_auth_token_valid_until = ""
        self.user_auth_token_refresh = ""
        self.user_is_tqs = False
        self.user_tqs_email = ""
        self.user_tqs_company = ""
        self.user_tqs_customers = []
        self.created_at = str(time.time())
        self.entity = "user"

    def update_user_customers(self):
        from utils.utils.Http import Http

        if self.user_is_tqs:
            user_response = Http().request(method="POST", url="https://login.tqs.com.br/oauth2/user", headers={"Authorization": "Bearer " + self.user_auth_token}, data={}, json_res=True)
            if user_response:
                self.user_tqs_customers = generate_user_tqs_customers(user_response["customers"])
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

    def update_user_datalist(self, model):
        no_more_model_builder = True
        no_more_model_work = True
        no_more_model_city_region = True
        no_more_model_category = True

        completed_models, last_evaluated_key = Dynamo().query_paginated_user_models_by_created_at(self.user_email, "completed", last_evaluated_key=None, limit=10000, reverse=False)
        for completed_model in completed_models:
            if completed_model["model_id"] != model["model_id"]:
                if model["model_builder"] == completed_model["model_builder"]:
                    no_more_model_builder = False

                if model["model_work"] == completed_model["model_work"]:
                    no_more_model_work = False

                if model["model_city_region"] == completed_model["model_city_region"]:
                    no_more_model_city_region = False

                if model["model_category"] == completed_model["model_category"]:
                    no_more_model_category = False

        if no_more_model_builder:
            if model["model_builder"] in self.user_model_datalist_builder:
                self.user_model_datalist_builder.remove(model["model_builder"])

        if no_more_model_work:
            if model["model_work"] in self.user_model_datalist_work:
                self.user_model_datalist_work.remove(model["model_work"])

        if no_more_model_city_region:
            if model["model_city_region"] in self.user_model_datalist_city_region:
                self.user_model_datalist_city_region.remove(model["model_city_region"])

        if no_more_model_category:
            if model["model_category"] in self.user_model_datalist_category:
                self.user_model_datalist_category.remove(model["model_category"])

        if no_more_model_builder or no_more_model_work or no_more_model_city_region or no_more_model_category:
            Dynamo().put_entity(self.__dict__)

    def update_last_login_at(self):
        if int(float(self.user_last_login_at)) + 3000 < int(time.time()):
            self.user_last_login_at = str(time.time())
            Dynamo().update_entity(self.__dict__, "user_last_login_at", self.user_last_login_at)

    def load_information(self):
        if not self.user_email:
            return
        user_data = Dynamo().get_user(self.user_email)
        if user_data:
            for attribute in user_data:
                setattr(self, attribute, user_data[attribute])

    def update_password(self, user_password, user_salt):
        password_item = UserPassword(self.user_email, EncodeDecode().encode_to_project_password(user_password, user_salt), user_salt)
        Dynamo().put_entity_into_crypto(password_item.__dict__)

    def check_if_password_is_corrected(self, user_password):
        password_item = Dynamo().get_entity_from_crypto({"pk": "user#" + self.user_email, "sk": "pass#" + self.user_email})
        if password_item:
            if "Item" in password_item:
                if "user_password" in password_item["Item"]:
                    if EncodeDecode().encode_to_project_password(user_password, password_item["Item"]["user_salt"]) == password_item["Item"]["user_password"]:
                        return True
        return False

    def update_auth_token(self, auth_token=None, auth_token_refresh=None, auth_token_valid_until=None):
        self.user_auth_token = auth_token
        if not auth_token:
            self.user_auth_token = str(uuid4())
        if auth_token_refresh:
            self.user_auth_token_refresh = auth_token_refresh
        if auth_token_valid_until:
            self.user_auth_token_valid_until = auth_token_valid_until

        auth_token = UserAuthToken(self.user_auth_token, self.user_email)
        # dynamo.update_entity(self.__dict__, "user_auth_token", self.user_auth_token)
        Dynamo().put_entity(self.__dict__)
        Dynamo().put_entity(auth_token.__dict__)

    def load_information_with_auth_token(self, user_auth_token):
        if not user_auth_token:
            return
        if user_auth_token:
            auth_token_item = Dynamo().get_auth_token(user_auth_token)
            if auth_token_item:
                self.user_email = auth_token_item["auth_user_email"]
        self.load_information()


def generate_user_tqs_customers(customers):
    # ignored_ids = [something]
    user_tqs_customers = []
    if customers:
        for customer in customers:
            # if company["id"] not in ignored_ids
            customer["id"] = "CUSTOMER-" + str(customer["id"])
            check_user = User(customer["id"])
            check_user.load_information()
            if check_user.user_status == "not_created":
                customer_user = User(str(customer["id"]))
                customer_user.user_status = "created"
                Dynamo().put_entity(customer_user.__dict__)
                customer_user.update_password(Generate().generate_long_id(), Generate().generate_salt(9))
            user_tqs_customers.append(customer)
    return user_tqs_customers
