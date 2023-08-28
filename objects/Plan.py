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
        self.plan_limit_federated_create = ""
        self.plan_limit_federated_filesize = ""
        self.plan_limit_ifc_download = ""
        self.plan_limit_ifc_open_filesize = ""
        self.plan_update_project = ""
        self.plan_limit_qr = ""
        self.plan_limit_share = ""
        self.plan_multiple_reference_trackers = ""
        self.plan_limit_teamplay = ""
        self.plan_limit_total_devices = ""
        self.plan_limit_device_changes_30d = ""
        self.plan_limit_account_per_device = ""
        self.plan_limit_days_offline = ""
        self.plan_start_date = ""
        self.plan_end_date = ""
        self.plan_order = ""
        self.plan_version = ""
        self.plan_show_countdown = ""

        self.created_at = str(time.time())
        self.entity = "plan"
