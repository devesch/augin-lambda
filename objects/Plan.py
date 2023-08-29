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
        self.plan_name = ""
        self.plan_shortname = ""
        self.plan_active = False
        self.plan_public = False
        self.plan_discount_enable = False
        self.plan_name_pt = ""
        self.plan_name_es = ""
        self.plan_name_en = ""
        self.plan_value = "00.00"
        self.plan_value_usd = "00.00"
        self.plan_installments = "00.00"
        self.plan_recurrence_months = "1"
        self.plan_stripe_plan_id = ""
        self.plan_stripe_price_br = ""
        self.plan_paypal_plan_id = ""
        self.plan_iugu_plan_code = ""
        self.plan_s2p_code = ""
        self.plan_limit_federated_create = ""  # se o cara pode ou não criar um projeto federado
        self.plan_limit_federated_filesize = ""  # limite do tamanho do federado
        self.plan_limit_ifc_download = ""  # se o cara pode baixar o arquivo IFC que ele fez o upload
        self.plan_limit_ifc_open_filesize = ""  # limite do tamanho que o cara pode abrir ou não TODO LIMITAR NO UPLOAD
        self.plan_update_project = ""  # se o user pode atualizar o projeto com outro modelo uploadado
        self.plan_limit_qr = ""  # se pode ou não ver o qrcode do modelo
        self.plan_limit_share = ""  # se pode ou não dar share no modelo
        self.plan_multiple_reference_trackers = ""  # se pode ter os trackers no modelo /
        self.plan_limit_teamplay = ""  # se pode ter os trackers no modelo / plan_teamplay_available_slots = "0"
        self.plan_limit_total_devices = ""  # plan_total_devices_slots = "0"
        self.plan_limit_device_changes_30d = ""  # plan_device_changes_30d_slots = "0"
        self.plan_limit_account_per_device = ""  # plan_maxium_differrent_acounts_per_device = "0"
        self.plan_limit_days_offline = ""  # plan_maxium_offline_days = "0"
        self.plan_start_date = ""
        self.plan_end_date = ""
        self.plan_order = "0"
        self.plan_version = "0"
        self.plan_show_countdown = ""

        self.created_at = str(time.time())
        self.entity = "plan"
