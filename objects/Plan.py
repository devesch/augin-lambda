import time
from uuid import uuid4
from utils.AWS.Dynamo import Dynamo
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.Generate import Generate
from objects.UserPassword import UserPassword
from objects.UserAuthToken import UserAuthToken


class Plan:
    def __init__(self, plan_id="") -> None:
        self.pk = "plan#" + plan_id
        self.sk = "plan#" + plan_id
        self.plan_id = plan_id

        self.plan_name_pt = ""
        self.plan_name_en = ""
        self.plan_name_es = ""
        self.plan_description_pt = ""
        self.plan_description_en = ""
        self.plan_description_es = ""
        self.plan_available_for_purchase = False
        self.plan_available_annually = False
        self.plan_price_annually_brl = "0"
        self.plan_price_annually_usd = "0"
        self.plan_price_annually_brl_actual = "0"
        self.plan_price_annually_usd_actual = "0"
        self.plan_price_annually_brl_actual_stripe_id = ""
        self.plan_price_annually_usd_actual_stripe_id = ""

        self.plan_annually_card_payment_method = False
        self.plan_annually_boleto_payment_method = False
        self.plan_annually_pix_payment_method = False
        self.plan_available_monthly = False
        self.plan_price_monthly_brl = "0"
        self.plan_price_monthly_usd = "0"
        self.plan_price_monthly_brl_actual = "0"
        self.plan_price_monthly_usd_actual = "0"
        self.plan_price_monthly_brl_actual_stripe_id = ""
        self.plan_price_monthly_usd_actual_stripe_id = ""

        self.plan_monthly_card_payment_method = False
        self.plan_cloud_space_in_mbs = "0"
        self.plan_maxium_model_size_in_mbs = "0"
        self.plan_maxium_federated_size_in_mbs = "0"
        self.plan_reference_tracker = "unavailable"  # unavailable, unique, multiple
        self.plan_maxium_devices_available = "1"
        self.plan_maxium_devices_changes_in_30d = "1"
        self.plan_has_trial = False
        self.plan_is_trial = False
        self.plan_trial_duration_in_days = "0"
        self.plan_app_can_be_offline_in_days = "0"

        self.plan_team_play_participants = "0"
        self.plan_download_files = False
        self.plan_share_files = False

        # self.plan_id = plan_id
        # self.plan_name = ""
        # self.plan_shortname = ""
        # self.plan_active = False
        # self.plan_public = False
        # self.plan_discount_enable = False
        # self.plan_name_pt = ""
        # self.plan_name_es = ""
        # self.plan_name_en = ""
        # self.plan_value = "00.00"
        # self.plan_value_usd = "00.00"
        # self.plan_installments = "00.00"
        # self.plan_recurrence_months = "1"
        # self.plan_stripe_plan_id = ""
        # self.plan_stripe_price_br = ""
        # self.plan_paypal_plan_id = ""
        # self.plan_iugu_plan_code = ""
        # self.plan_s2p_code = ""
        # self.plan_limit_federated_create = ""  # se o cara pode ou não criar um projeto federado
        # self.plan_limit_federated_filesize = ""  # limite do tamanho do federado
        # self.plan_limit_ifc_download = ""  # se o cara pode baixar o arquivo IFC que ele fez o upload
        # self.plan_limit_ifc_open_filesize = ""  # limite do tamanho que o cara pode abrir ou não TODO LIMITAR NO UPLOAD
        # self.plan_update_project = ""  # se o user pode atualizar o projeto com outro modelo uploadado
        # self.plan_limit_qr = ""  # se pode ou não ver o qrcode do modelo
        # self.plan_limit_share = ""  # se pode ou não dar share no modelo
        # self.plan_multiple_reference_trackers = ""  # se pode ter os trackers no modelo /
        # self.plan_limit_teamplay = ""  # se pode ter os trackers no modelo / plan_teamplay_available_slots = "0"
        # self.plan_limit_total_devices = ""  # plan_total_devices_slots = "0"
        # self.plan_limit_device_changes_30d = ""  # plan_device_changes_30d_slots = "0"
        # self.plan_limit_account_per_device = ""  # plan_maxium_differrent_acounts_per_device = "0"
        # self.plan_limit_days_offline = ""  # plan_maxium_offline_days = "0"
        # self.plan_start_date = ""
        # self.plan_end_date = ""
        # self.plan_order = "0"
        # self.plan_version = "0"
        # self.plan_show_countdown = ""

        self.created_at = str(time.time())
        self.entity = "plan"


def translate_reference_tracker(plan_reference_tracker):
    from utils.Config import lambda_constants

    for reference_tracker_name, reference_tracker_value in lambda_constants["plan_reference_trackers"].items():
        if plan_reference_tracker == reference_tracker_value:
            return reference_tracker_name.title()


def generate_plans_hierarchy(plans):
    plans_hierarchy = {}
    if plans:
        for plan in plans:
            plans_hierarchy[plan["plan_id"] + "-annually"] = int(plan["plan_price_annually_brl"])
            plans_hierarchy[plan["plan_id"] + "-monthly"] = int(plan["plan_price_monthly_brl"]) * 8
    return plans_hierarchy


def generate_plan_price_with_coupon_discount(plan, coupon_code, plan_recurrency, currency):
    coupom = Dynamo().get_coupon(coupon_code)
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
