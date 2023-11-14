import time
from utils.utils.Generate import Generate
from utils.AWS.Dynamo import Dynamo
from utils.Code import Code


class UserNotification:
    def __init__(self, user_id, notification_id) -> None:
        self.pk = "user#" + user_id
        self.sk = "notification#" + notification_id
        self.notification_user_id = user_id
        self.notification_id = notification_id

        self.notification_message_pt = ""
        self.notification_message_en = ""
        self.notification_message_es = ""
        self.notification_redirect = ""

        self.created_at = str(time.time())
        self.entity = "notification"


def create_notification_model_processed(user_id, model_name):
    notification = UserNotification(user_id, Generate().generate_long_id()).__dict__
    notification["notification_message_pt"] = Code().translate("Seu arquivo", "pt") + " " + model_name + " " + Code().translate("foi processado com sucesso.", "pt")
    notification["notification_message_en"] = Code().translate("Seu arquivo", "en") + " " + model_name + " " + Code().translate("foi processado com sucesso.", "en")
    notification["notification_message_es"] = Code().translate("Seu arquivo", "es") + " " + model_name + " " + Code().translate("foi processado com sucesso.", "es")
    notification["notification_redirect"] = "panel_explore_project"
    Dynamo().put_entity(notification)
