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


# TODO: matheus function
def create_notification_model_processing(user_id, model_name):
    notification = UserNotification(user_id, Generate().generate_long_id()).__dict__
    notification["notification_message_pt"] = Code().translate("Seu arquivo", "pt") + " " + model_name + " " + Code().translate("está sendo processado. Você será notificado quando estiver concluído.", "pt")
    notification["notification_message_en"] = Code().translate("Seu arquivo", "en") + " " + model_name + " " + Code().translate("está sendo processado. Você será notificado quando estiver concluído.", "en")
    notification["notification_message_es"] = Code().translate("Seu arquivo", "es") + " " + model_name + " " + Code().translate("está sendo processado. Você será notificado quando estiver concluído.", "es")
    notification["notification_redirect"] = "panel_explore_project"
    Dynamo().put_entity(notification)


def create_notification_model_processed(user_id, model_name):
    notification = UserNotification(user_id, Generate().generate_long_id()).__dict__
    notification["notification_message_pt"] = Code().translate("Seu arquivo", "pt") + " " + model_name + " " + Code().translate("foi processado com sucesso.", "pt")
    notification["notification_message_en"] = Code().translate("Seu arquivo", "en") + " " + model_name + " " + Code().translate("foi processado com sucesso.", "en")
    notification["notification_message_es"] = Code().translate("Seu arquivo", "es") + " " + model_name + " " + Code().translate("foi processado com sucesso.", "es")
    notification["notification_redirect"] = "panel_explore_project"
    Dynamo().put_entity(notification)


def create_notification_trial_started(user_id):
    notification = UserNotification(user_id, Generate().generate_long_id()).__dict__
    notification["notification_message_pt"] = Code().translate("Seu trial foi iniciado com sucesso.", "pt")
    notification["notification_message_en"] = Code().translate("Seu trial foi iniciado com sucesso.", "en")
    notification["notification_message_es"] = Code().translate("Seu trial foi iniciado com sucesso.", "es")
    notification["notification_redirect"] = "panel_your_plan"
    Dynamo().put_entity(notification)


def create_notification_trial_ended(user_id):
    notification = UserNotification(user_id, Generate().generate_long_id()).__dict__
    notification["notification_message_pt"] = Code().translate("Seu trial terminou, escolha seu plano.", "pt")
    notification["notification_message_en"] = Code().translate("Seu trial terminou, escolha seu plano.", "en")
    notification["notification_message_es"] = Code().translate("Seu trial terminou, escolha seu plano.", "es")
    notification["notification_redirect"] = "checkout_upgrade_your_plan"
    Dynamo().put_entity(notification)


def create_notification_new_device_accessed(user_id):
    notification = UserNotification(user_id, Generate().generate_long_id()).__dict__
    notification["notification_message_pt"] = Code().translate("Um novo dispositivo foi usado para acessar sua conta.", "pt")
    notification["notification_message_en"] = Code().translate("Um novo dispositivo foi usado para acessar sua conta.", "en")
    notification["notification_message_es"] = Code().translate("Um novo dispositivo foi usado para acessar sua conta.", "es")
    notification["notification_redirect"] = "panel_devices"
    Dynamo().put_entity(notification)


# TODO:
def create_notification_payment_failed(user_id):
    notification = UserNotification(user_id, Generate().generate_long_id()).__dict__
    notification["notification_message_pt"] = Code().translate("Houve uma falha ao cobrar sua assinatura. Atualize seus métodos de pagamento.", "pt")
    notification["notification_message_en"] = Code().translate("Houve uma falha ao cobrar sua assinatura. Atualize seus métodos de pagamento.", "en")
    notification["notification_message_es"] = Code().translate("Houve uma falha ao cobrar sua assinatura. Atualize seus métodos de pagamento.", "es")
    notification["notification_redirect"] = "panel_devices"
    Dynamo().put_entity(notification)

def create_notification_payment_success(user_id):
    notification = UserNotification(user_id, Generate().generate_long_id()).__dict__
    notification["notification_message_pt"] = Code().translate("Seu pagamento foi realizado com sucesso.", "pt")
    notification["notification_message_en"] = Code().translate("Seu pagamento foi realizado com sucesso.", "en")
    notification["notification_message_es"] = Code().translate("Seu pagamento foi realizado com sucesso.", "es")
    notification["notification_redirect"] = "panel_your_plan"
    Dynamo().put_entity(notification)

# TODO:
def create_notification_card_will_expire(user_id, card_number):
    notification = UserNotification(user_id, Generate().generate_long_id()).__dict__
    notification["notification_message_pt"] = Code().translate("Seu cartão" + " " + card_number + " " + "expira em breve, atualize seus métodos de pagamento.", "pt")
    notification["notification_message_en"] = Code().translate("Seu cartão" + " " + card_number + " " + "expira em breve, atualize seus métodos de pagamento.", "en")
    notification["notification_message_es"] = Code().translate("Seu cartão" + " " + card_number + " " + "expira em breve, atualize seus métodos de pagamento.", "es")
    notification["notification_redirect"] = "panel_devices"
    Dynamo().put_entity(notification)

def create_notification_model_shared_with_me(user_id, model_name):
    notification = UserNotification(user_id, Generate().generate_long_id()).__dict__
    notification["notification_message_pt"] = Code().translate("Arquivo", "pt") + " " + model_name + " " + Code().translate("foi adicionado aos projetos compartilhados.", "pt")
    notification["notification_message_en"] = Code().translate("Arquivo", "en") + " " + model_name + " " + Code().translate("foi adicionado aos projetos compartilhados.", "en")
    notification["notification_message_es"] = Code().translate("Arquivo", "es") + " " + model_name + " " + Code().translate("foi adicionado aos projetos compartilhados.", "es")
    notification["notification_redirect"] = "panel_shared_project"
    Dynamo().put_entity(notification)