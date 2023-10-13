from utils.AWS.Dynamo import Dynamo
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.Generate import Generate
from utils.utils.Validation import Validation
from utils.utils.Date import Date
from objects.UserPassword import UserPassword
from objects.UserAuthToken import UserAuthToken
from objects.UserSubscription import UserSubscription
from objects.UserDevice import UserDevice, reconnect_device
from objects.UserFolder import UserFolder, add_file_to_folder, remove_file_from_folder, add_folder_to_folder, remove_folder_from_folder
from utils.utils.Sort import Sort
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.controllers.stripe_controller import StripeController
from utils.Config import lambda_constants
import uuid
import time


class User:
    def __init__(self, user_id="") -> None:
        self.pk = "user#" + user_id
        self.sk = "user#" + user_id
        self.user_email = ""
        self.user_id = user_id

        self.user_name = ""
        self.user_thumb = ""
        self.user_first_three_letters_name = ""
        self.user_status = "not_created"
        self.user_phone = ""
        self.user_cpf = ""
        self.user_cnpj = ""
        self.user_address_data = {"user_country": "BR", "user_zip_code": "", "user_state": "", "user_city": "", "user_city_code": "", "user_street": "", "user_neighborhood": "", "user_street_number": "", "user_complement": ""}
        self.user_client_type = "physical"  # physical / company / international
        self.user_aggre_with_communication = False
        self.user_credential = ""
        self.user_ip = ""
        self.user_cart_currency = ""
        self.user_cart_coupon_code = ""

        self.user_dicts_folder_id = ""
        self.user_shared_dicts_folder_id = ""

        self.user_used_cloud_space_in_mbs = "0.0"
        self.user_favorited_models = []
        self.user_favorited_folders = []
        self.user_plan_id = ""
        self.user_subscription_id = ""
        self.user_subscription_valid_until = ""
        self.user_subscription_status = "none"
        self.user_used_trials = []
        self.user_stripe_customer_id = ""
        self.user_payment_ready = False
        self.user_pagination_count = "50"

        self.user_last_login_at = str(time.time())
        self.created_at = str(time.time())
        self.entity = "user"

    def delete_account(self):
        user_dicts_folder = Dynamo().get_folder(self.user_dicts_folder_id)
        if user_dicts_folder:
            self.delete_folder(user_dicts_folder)

        not_deleted_models = []
        not_deleted_models.extend(Dynamo().query_user_models_from_state(self, "not_created"))
        not_deleted_models.extend(Dynamo().query_user_models_from_state(self, "in_processing"))
        not_deleted_models.extend(Dynamo().query_user_models_from_state(self, "completed"))
        if not_deleted_models:
            for model in not_deleted_models:
                ModelController().delete_model(model, self)

        deleted_short_id = "deleted_" + Generate().generate_short_id()
        self.user_email = deleted_short_id + "@" + deleted_short_id + ".com"
        self.user_name = deleted_short_id
        self.user_thumb = ""
        self.user_first_three_letters_name = "999"
        self.user_status = "deleted"
        self.user_phone = ""
        self.user_cpf = ""
        self.user_cnpj = ""
        self.user_address_data = {"user_country": "BR", "user_zip_code": "", "user_state": "", "user_city": "", "user_city_code": "", "user_street": "", "user_neighborhood": "", "user_street_number": "", "user_complement": ""}
        self.user_client_type = "physical"  # physical / company / international
        self.user_aggre_with_communication = False
        self.user_credential = ""
        self.user_ip = str(time.time())
        self.user_dicts_folder_id = ""
        self.user_shared_dicts_folder_id = ""
        self.user_subscription_status = "none"
        self.user_payment_ready = False
        Dynamo().put_entity(self.__dict__)
        self.clear_all_auth_tokens()

    def decrease_used_cloud_space_in_mbs(self, new_value_for_decrease_in_mbs):
        new_user_used_cloud_space_in_mbs = str(float(self.user_used_cloud_space_in_mbs) - float(new_value_for_decrease_in_mbs))
        if float(new_user_used_cloud_space_in_mbs) < 0:
            new_user_used_cloud_space_in_mbs = "0.0"
        self.update_attribute("user_used_cloud_space_in_mbs", str(new_user_used_cloud_space_in_mbs))

    def increase_used_cloud_space_in_mbs(self, new_value_for_increase_in_mbs):
        self.update_attribute("user_used_cloud_space_in_mbs", str(float(self.user_used_cloud_space_in_mbs) + float(new_value_for_increase_in_mbs)))

    def connect_device(self, new_device_data):
        user_device = Dynamo().get_user_device(self.user_id, new_device_data["device_id"])
        if not user_device:
            new_device = UserDevice(self.user_id, new_device_data["device_id"], new_device_data["device_name"], new_device_data["device_model"], new_device_data["device_os"]).__dict__
            Dynamo().put_entity(new_device)
            return new_device

        reconnect_device(user_device)
        return user_device

    def update_attribute(self, attribute, new_value):
        setattr(self, attribute, new_value)
        Dynamo().update_entity(self.__dict__, attribute, new_value)
        if attribute in ("user_name", "user_phone", "user_email") and self.user_stripe_customer_id:
            StripeController().update_customer(self.user_stripe_customer_id, self)

    def generate_user_thumb_url(self):
        if self.user_thumb:
            return lambda_constants["processed_bucket_cdn"] + "/" + self.user_thumb
        else:
            return lambda_constants["cdn"] + "/assets/icons/person_square.svg"

    def remove_user_cart_coupon_code(self):
        self.user_cart_coupon_code = ""
        Dynamo().update_entity(self.__dict__, "user_cart_coupon_code", self.user_cart_coupon_code)

    def check_if_already_used_coupom(self, coupon):
        return bool(Dynamo().get_used_coupon(coupon["coupon_code"], self.user_id))

    def generate_plan_price_with_coupon_discount(self, plan, plan_recurrency, currency):
        coupom = Dynamo().get_coupon(self.user_cart_coupon_code)
        new_plan_price = None
        coupon_discount_value = None

        if not coupom:
            return None, None

        if coupom["coupon_discount_type"] == "total":
            if plan_recurrency == "annually":
                if currency == "brl":
                    new_plan_price = int(plan["plan_price_annually_brl"]) - int(coupom["coupon_brl_discount"])
                    coupon_discount_value = int(coupom["coupon_brl_discount"])
                if currency == "usd":
                    new_plan_price = int(plan["plan_price_annually_usd"]) - int(coupom["coupon_usd_discount"])
                    coupon_discount_value = int(coupom["coupon_usd_discount"])

            if plan_recurrency == "monthly":
                if currency == "brl":
                    new_plan_price = int(plan["plan_price_monthly_brl"]) - int(coupom["coupon_brl_discount"])
                    coupon_discount_value = int(coupom["coupon_brl_discount"])
                if currency == "usd":
                    new_plan_price = int(plan["plan_price_monthly_usd"]) - int(coupom["coupon_usd_discount"])
                    coupon_discount_value = int(coupom["coupon_usd_discount"])

        elif coupom["coupon_discount_type"] == "percentage":
            if plan_recurrency == "annually":
                if currency == "brl":
                    coupon_discount_value = int(int(plan["plan_price_annually_brl"]) * float(int(coupom["coupon_percentage_discount"]) / 100))
                    new_plan_price = int(int(plan["plan_price_annually_brl"]) - coupon_discount_value)
                if currency == "usd":
                    coupon_discount_value = int(int(plan["plan_price_annually_usd"]) * float(int(coupom["coupon_percentage_discount"]) / 100))
                    new_plan_price = int(int(plan["plan_price_annually_usd"]) - coupon_discount_value)

            if plan_recurrency == "monthly":
                if currency == "brl":
                    coupon_discount_value = int(int(plan["plan_price_monthly_brl"]) * float(int(coupom["coupon_percentage_discount"]) / 100))
                    new_plan_price = int(int(plan["plan_price_monthly_brl"]) - coupon_discount_value)
                if currency == "usd":
                    coupon_discount_value = int(int(plan["plan_price_monthly_usd"]) * float(int(coupom["coupon_percentage_discount"]) / 100))
                    new_plan_price = int(int(plan["plan_price_monthly_usd"]) - coupon_discount_value)

        return str(new_plan_price), str(coupon_discount_value)

    def active_trial_plan(self, trial_plan):
        user_subscription_id = "trial-" + Generate().generate_short_id()
        user_subscription = UserSubscription(user_subscription_id, self.user_id).__dict__
        user_subscription["subscription_plan_id"] = trial_plan["plan_id"]
        user_subscription["subscription_recurrency"] = ""
        user_subscription["subscription_status"] = "active"
        user_subscription["subscription_default_payment_method"] = ""
        user_subscription["subscription_price"] = "0000"
        user_subscription["subscription_currency"] = self.user_cart_currency
        user_subscription["subscription_currency"] = self.user_cart_currency
        user_subscription["subscription_last_order_id"] = ""
        user_subscription["subscription_valid_until"] = str(Date().add_days_to_current_unix_time(trial_plan["plan_trial_duration_in_days"]))
        user_subscription["subscription_is_trial"] = True
        Dynamo().put_entity(user_subscription)

        self.user_subscription_id = user_subscription_id
        self.user_subscription_valid_until = user_subscription["subscription_valid_until"]
        self.user_subscription_status = "active"
        self.user_plan_id = trial_plan["plan_id"]
        self.user_used_trials.append(trial_plan["plan_id"])
        Dynamo().put_entity(self.__dict__)

    def cancel_current_subscription(self, valid_until_now=False):
        user_subscription = Dynamo().get_subscription(self.user_subscription_id)
        StripeController().cancel_subscription(self.user_subscription_id)
        stripe_subscription = StripeController().get_subscription(self.user_subscription_id)
        user_subscription["subscription_status"] = stripe_subscription["status"]
        user_subscription["subscription_canceled_at"] = str(stripe_subscription["canceled_at"])
        if valid_until_now:
            user_subscription["subscription_valid_until"] = str(time.time())
        Dynamo().put_entity(user_subscription)
        if valid_until_now:
            self.update_attribute("user_subscription_valid_until", user_subscription["subscription_valid_until"])
        self.update_attribute("user_subscription_status", stripe_subscription["status"])

    def get_user_actual_plan(self):
        if self.check_if_subscription_is_valid():
            return Dynamo().get_plan(self.user_plan_id)
        else:
            return Dynamo().get_free_plan()

    def check_if_subscription_is_valid(self):
        if not self.user_subscription_valid_until:
            return False
        return float(self.user_subscription_valid_until) > float(time.time())

    def update_subscription(self, order, user_stripe_subscription):
        user_subscription = Dynamo().get_subscription(user_stripe_subscription.stripe_id)
        if not user_subscription:
            user_subscription = UserSubscription(user_stripe_subscription.stripe_id, self.user_id).__dict__

        user_subscription["subscription_plan_id"] = order["order_plan_id"]
        user_subscription["subscription_recurrency"] = order["order_plan_recurrency"]
        user_subscription["subscription_status"] = user_stripe_subscription["status"]
        user_subscription["subscription_default_payment_method"] = user_stripe_subscription["default_payment_method"]
        user_subscription["subscription_price_id"] = user_stripe_subscription["plan"]["id"]
        user_subscription["subscription_price"] = user_stripe_subscription["plan"]["amount_decimal"]
        user_subscription["subscription_currency"] = user_stripe_subscription["currency"]
        user_subscription["subscription_last_order_id"] = order["order_id"]
        user_subscription["subscription_valid_until"] = str(user_stripe_subscription["current_period_end"])
        Dynamo().put_entity(user_subscription)

        self.user_subscription_id = user_stripe_subscription.stripe_id
        self.user_subscription_valid_until = user_subscription["subscription_valid_until"]
        self.user_subscription_status = user_stripe_subscription["status"]
        self.user_plan_id = order["order_plan_id"]
        Dynamo().put_entity(self.__dict__)

    def clear_all_auth_tokens(self):
        all_users_auth_tokens = Dynamo().query_users_auth_token(self.user_id)
        if all_users_auth_tokens:
            for auth_token in all_users_auth_tokens:
                Dynamo().delete_entity(auth_token)

    def clear_perdonal_data(self):
        self.user_address_data = {"user_country": "", "user_zip_code": "", "user_state": "", "user_city": "", "user_city_code": "", "user_street": "", "user_neighborhood": "", "user_street_number": "", "user_complement": ""}

    def add_folder_to_user_shared_dicts(self, user_shared_dicts, folder):
        if folder["folder_id"] not in user_shared_dicts["folders"]:
            user_shared_dicts["folders"].append(folder["folder_id"])
            Dynamo().put_entity(user_shared_dicts)

    def remove_folder_from_user_shared_dicts(self, folder_id):
        user_shared_dicts = Dynamo().get_folder(self.user_shared_dicts_folder_id)
        if folder_id in user_shared_dicts["folders"]:
            user_shared_dicts["folders"].remove(folder_id)
            Dynamo().put_entity(user_shared_dicts)

    def remove_model_from_user_shared_dicts(self, model_id):
        user_shared_dicts = Dynamo().get_folder(self.user_shared_dicts_folder_id)
        if model_id in user_shared_dicts["files"]:
            user_shared_dicts["files"].remove(model_id)
            Dynamo().put_entity(user_shared_dicts)

    def remove_folder_id_from_favorites(self, folder_id):
        if folder_id in self.user_favorited_folders:
            self.user_favorited_folders.remove(folder_id)
            Dynamo().put_entity(self.__dict__)

    def add_folder_id_to_favorites(self, folder_id):
        if folder_id not in self.user_favorited_folders:
            self.user_favorited_folders.append(folder_id)
            Dynamo().put_entity(self.__dict__)

    def remove_model_id_from_favorites(self, model_id):
        if model_id in self.user_favorited_models:
            self.user_favorited_models.remove(model_id)
            Dynamo().put_entity(self.__dict__)

    def add_model_id_to_favorites(self, model_id):
        if model_id not in self.user_favorited_models:
            self.user_favorited_models.append(model_id)
            Dynamo().put_entity(self.__dict__)

    def move_folder_to_another_folder(self, folder, destiny_folder=""):
        if folder["folder_root_id"]:
            root_folder = Dynamo().get_folder(folder["folder_root_id"])
            remove_folder_from_folder(root_folder, folder)

        if not destiny_folder:
            destiny_folder = Dynamo().get_folder(self.user_dicts_folder_id)
        add_folder_to_folder(destiny_folder, folder)

    def move_model_to_another_folder(self, model, new_folder=""):
        model_folder = Dynamo().get_folder(model["model_folder_id"])
        remove_file_from_folder(model_folder, model["model_id"], model["model_filesize"])

        if not new_folder:
            new_folder = Dynamo().get_folder(self.user_dicts_folder_id)

        model["model_folder_id"] = new_folder["folder_id"]
        Dynamo().update_entity(model, "model_folder_id", model["model_folder_id"])

        add_file_to_folder(new_folder, model["model_id"], model["model_filesize"])

    def create_new_folder(self, new_folder_name, root_folder_id="", is_user_root_folder=False):
        if not is_user_root_folder:
            if root_folder_id:
                root_folder = Dynamo().get_folder(root_folder_id)
            else:
                root_folder = Dynamo().get_folder(self.user_dicts_folder_id)

            folder_path = root_folder["folder_path"] + "/" if root_folder else ""
            parent_id = root_folder["folder_id"] if root_folder else ""
        else:
            folder_path = ""
            parent_id = ""

        new_folder = UserFolder(self.user_id, Generate().generate_short_id(), new_folder_name, folder_path, parent_id).__dict__
        new_folder["folder_share_link"] = f'{lambda_constants["domain_name_url"]}/view_folder/?folder_id={new_folder["folder_id"]}'
        new_folder["folder_share_link_qrcode"] = f'{lambda_constants["processed_bucket_cdn"]}/folders_qrcodes/{new_folder["folder_id"]}.png'
        Generate().generate_qr_code(new_folder["folder_share_link"], lambda_constants["processed_bucket"], f'folders_qrcodes/{new_folder["folder_id"]}.png')
        Dynamo().put_entity(new_folder)

        if not is_user_root_folder:
            root_folder["folders"].append(new_folder["folder_id"])
            Dynamo().put_entity(root_folder)

        return new_folder

    def delete_folder(self, folder):
        if folder["folders"]:
            for sub_folder_id in folder["folders"]:
                sub_folder = Dynamo().get_folder(sub_folder_id)
                if sub_folder:
                    self.delete_folder(sub_folder)

        if folder["files"]:
            for model_id in folder["files"]:
                model = Dynamo().get_model(model_id)
                if model:
                    ModelController().delete_model(model, self)

        root_folder = Dynamo().get_folder(folder["folder_root_id"])
        if root_folder:
            root_folder["folders"].remove(folder["folder_id"])
            Dynamo().put_entity(root_folder)

        Dynamo().delete_entity(folder)

    def add_model_to_user_dicts(self, model, shared=False):
        if shared:
            user_folder = Dynamo().get_folder(self.user_shared_dicts_folder_id)
        else:
            user_folder = Dynamo().get_folder(self.user_dicts_folder_id)

        user_folder["files"].append(model["model_id"])
        Dynamo().put_entity(user_folder)

    def remove_model_from_user_dicts(self, model, shared=False):
        model_folder = Dynamo().get_folder(model["model_folder_id"])
        if model_folder:
            remove_file_from_folder(model_folder, model["model_id"], model["model_filesize"])
            if not model["model_is_federated"] and not shared:
                self.user_used_cloud_space_in_mbs = str(float(self.user_used_cloud_space_in_mbs) - float(ModelController().convert_model_filesize_to_mb(model["model_filesize"])))
            Dynamo().put_entity(self.__dict__)

    def update_last_login_at(self, user_ip):
        if int(float(self.user_last_login_at)) + 3000 < float(time.time()):
            self.update_attribute("user_last_login_at", str(time.time()))

    def check_if_is_payment_ready(self):
        self.user_payment_ready = True

        if not self.user_name:
            self.user_payment_ready = False
        if not self.user_phone:
            self.user_payment_ready = False

        if not self.user_address_data["user_country"]:
            self.user_payment_ready = False
        if not self.user_address_data["user_zip_code"]:
            self.user_payment_ready = False
        if not self.user_address_data["user_state"]:
            self.user_payment_ready = False
        if not self.user_address_data["user_city"]:
            self.user_payment_ready = False
        if not self.user_address_data["user_neighborhood"]:
            self.user_payment_ready = False

        if self.user_client_type == "physical" or self.user_client_type == "company":
            if not self.user_address_data["user_city_code"]:
                self.user_payment_ready = False
            if not self.user_address_data["user_street"]:
                self.user_payment_ready = False
            if not self.user_address_data["user_street_number"]:
                self.user_payment_ready = False

        if self.user_client_type == "physical":
            if not self.user_cpf:
                self.user_payment_ready = False
        elif self.user_client_type == "company":
            if not self.user_cnpj:
                self.user_payment_ready = False

        if not self.user_payment_ready:
            return False

        if not self.user_stripe_customer_id:
            self.user_stripe_customer_id = StripeController().create_customer(self)
        else:
            StripeController().update_customer(self.user_stripe_customer_id, self)
            return True

    def recreate_stripe_user(self):
        new_user_stripe_customer_id = StripeController().create_customer(self)
        self.update_attribute("user_stripe_customer_id", new_user_stripe_customer_id)

    def update_cart_currency(self):
        if self.user_address_data["user_country"] == "BR":
            self.user_cart_currency = "brl"
        elif self.user_address_data["user_country"] != "BR":
            self.user_cart_currency = "usd"

    def load_information(self):
        if not self.user_id:
            return
        user_data = Dynamo().get_user(self.user_id)
        if user_data:
            for attribute in user_data:
                setattr(self, attribute, user_data[attribute])
        self.update_cart_currency()

    def update_auth_token(self):
        self.user_last_login_at = str(time.time())
        self.user_auth_token = str(uuid.uuid4())
        auth_token = UserAuthToken(self.user_auth_token, self.user_id)
        Dynamo().put_entity(self.__dict__)
        Dynamo().put_entity(auth_token.__dict__)

    def check_if_password_is_corrected(self, user_password):
        password_item = Dynamo().get_entity_from_crypto({"pk": "user#" + self.user_id, "sk": "pass#" + self.user_id})
        if password_item:
            if "Item" in password_item:
                if "user_password" in password_item["Item"]:
                    if EncodeDecode().encode_to_project_password(user_password, password_item["Item"]["user_salt"]) == password_item["Item"]["user_password"]:
                        return True
        return False

    def update_password(self, user_password, user_salt):
        password_item = UserPassword(self.user_id, EncodeDecode().encode_to_project_password(user_password, user_salt), user_salt)
        Dynamo().put_entity_into_crypto(password_item.__dict__)


def sort_user_folders(user, user_folders, sort_attribute="folder_name", sort_reverse=False):
    sort_reverse = sort_reverse == "True"

    if not sort_attribute:
        sort_attribute = "folder_name"
    if sort_attribute == "model_name":
        sort_attribute = "folder_name"
    if sort_attribute == "model_filesize":
        sort_attribute = "folder_foldersize_in_mbs"

    favorited_folders = []
    normal_folders = []
    sorted_folders = []
    if user_folders:
        for folder in user_folders:
            if user and folder["folder_id"] in user.user_favorited_folders:
                sorted_folders.append(folder)
            else:
                normal_folders.append(folder)

    if sort_attribute in ["created_at", "folder_foldersize_in_mbs"]:
        sort_reverse = not sort_reverse
    if sort_attribute in ["folder_name", "owners_name"]:
        favorited_folders = Sort().sort_dict_list(favorited_folders, sort_attribute, reverse=sort_reverse, integer=False)
        normal_folders = Sort().sort_dict_list(normal_folders, sort_attribute, reverse=sort_reverse, integer=False)
    else:
        favorited_folders = Sort().sort_dict_list(favorited_folders, sort_attribute, reverse=sort_reverse, integer=True)
        normal_folders = Sort().sort_dict_list(normal_folders, sort_attribute, reverse=sort_reverse, integer=True)

    sorted_folders.extend(favorited_folders)
    sorted_folders.extend(normal_folders)
    return sorted_folders


def load_user(user_id):
    if not user_id:
        return None
    if Validation().check_if_is_uuid4(user_id):
        auth_token_item = Dynamo().get_auth_token(user_id)
        if auth_token_item:
            user_id = auth_token_item["auth_user_id"]
        else:
            user_id = None
    elif "@" in user_id:
        user_id = Dynamo().get_user_id_with_email(user_id)
    if not user_id:
        return None
    user = User(user_id)
    user.load_information()
    if user.user_status in ("not_created", "deleted"):
        user = None
    return user
