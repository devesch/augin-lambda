from utils.AWS.Dynamo import Dynamo
from time import time


class BackofficeData:
    def __init__(self) -> None:
        self.pk = "backoffice#"
        self.sk = "backoffice#"
        self.backoffice_data_total_user_count = "0"
        self.backoffice_data_total_order_count = "0"
        self.backoffice_data_total_model_count = "0"
        self.backoffice_data_total_coupon_count = "0"
        self.backoffice_data_total_product_count = "0"
        self.backoffice_data_total_cart_abandonment_count = "0"
        self.backoffice_data_total_recurrence_failure_count = "0"
        self.backoffice_data_total_cancel_subscription_count = "0"
        self.backoffice_data_total_page = {}
        self.created_at = str(time())
        self.entity = "backoffice_data"


def fix_backoffice_data_total_count(backoffice_data):
    for key, val in backoffice_data.items():
        if "backoffice_data_total_" in key:
            every_object_from_entity = Dynamo().query_entity(key.replace("backoffice_data_total_", "").replace("_count", ""))
            backoffice_data[key] = str(len(every_object_from_entity))
    Dynamo().put_entity(backoffice_data)


def increase_backoffice_data_total_count(entity):
    backoffice_data = get_backoffice_data()
    key = "backoffice_data_total_" + entity + "_count"
    if key not in backoffice_data:
        backoffice_data[key] = "0"
    backoffice_data[key] = str(int(backoffice_data[key]) + 1)
    Dynamo().update_entity(backoffice_data, key, backoffice_data[key])


def get_backoffice_data():
    backoffice_data = Dynamo().get_backoffice_data()
    if not backoffice_data:
        backoffice_data = BackofficeData().__dict__
        Dynamo().put_entity(backoffice_data)
    return backoffice_data
