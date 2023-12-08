from objects.UserDevice import disconnect_device, generate_connected_and_disconnected_devices, generate_disconnected_devices_in_last_30d
from python_web_frame.controllers.stripe_controller import StripeController
from python_web_frame.controllers.model_controller import ModelController
from objects.BackofficeData import increase_backoffice_data_total_count
from objects.UserFolder import check_if_folder_movement_is_valid
from objects.CancelSubscription import CancelSubscription
from objects.UserPaymentMethod import UserPaymentMethod
from python_web_frame.panel_page import PanelPage
from utils.utils.EncodeDecode import EncodeDecode
from python_web_frame.user_page import UserPage
from utils.utils.Validation import Validation
from utils.utils.Generate import Generate
from utils.Config import lambda_constants
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Lambda import Lambda
from objects.User import load_user
from utils.AWS.S3 import S3
import time
from objects.UserNotification import create_notification_model_shared_with_me


class UpdateUser(UserPage, PanelPage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "Nenhum command no post"}

        if self.post["command"] not in ("get_root_folder", "add_shared"):
            if not self.user:
                return {"error": "Nenhum usuário encontrado"}

        return getattr(self, self.post["command"])()

    def delete_user_thumb(self):
        self.user.update_attribute("user_thumb", "")
        return {"success": "Thumb removida com sucesso"}

    def update_password(self):
        if not self.post.get("user_current_password"):
            return {"error": "É necessário informar a senha atual."}
        if not self.post.get("user_password"):
            return {"error": "É necessário informar a nova senha."}
        if not Validation().check_if_password(self.post["user_password"]):
            return {"error": "A senha deve ter entre 8 e 45 caracteres."}

        self.user.update_password(self.post["user_password"], Generate().generate_salt(9))
        return {"success": "Senha alterada com sucesso"}

    def update_international_data(self):
        if not self.post.get("user_zip_code"):
            return {"error": "É necessário informar um código ZIP."}
        if not self.post.get("user_state"):
            return {"error": "É necessário informar um estado."}
        if not self.post.get("user_city"):
            return {"error": "É necessário informar uma cidade."}
        if not self.post.get("user_city_code"):
            return {"error": "É necessário informar um código de cidade."}
        if not self.post.get("user_neighborhood"):
            return {"error": "É necessário informar um bairro."}
        if not self.post.get("user_street"):
            return {"error": "É necessário informar uma rua."}

        self.user.user_address_data["user_zip_code"] = self.post["user_zip_code"]
        self.user.user_address_data["user_state"] = self.post["user_state"].upper()
        self.user.user_address_data["user_city"] = self.post["user_city"].title()
        self.user.user_address_data["user_city_code"] = self.post["user_city_code"].capitalize()
        self.user.user_address_data["user_neighborhood"] = self.post["user_neighborhood"].title()
        self.user.user_address_data["user_street"] = self.post["user_street"].title()
        self.user.user_client_type = "international"
        self.user_address_data_last_update = str(time.time())
        Dynamo().put_entity(self.user.__dict__)
        return {"success": "Dados atualizados com sucesso"}

    def update_cnpj_data(self):
        if not self.post.get("user_cnpj"):
            return {"error": "É necessário informar um CNPJ."}
        if not self.post.get("user_zip_code"):
            return {"error": "É necessário informar um código ZIP."}
        if not self.post.get("user_state"):
            return {"error": "É necessário informar um estado."}
        if not self.post.get("user_city"):
            return {"error": "É necessário informar uma cidade."}
        if not self.post.get("user_city_code"):
            return {"error": "É necessário informar um código de cidade."}
        if not self.post.get("user_neighborhood"):
            return {"error": "É necessário informar um bairro."}
        if not self.post.get("user_street"):
            return {"error": "É necessário informar uma rua."}
        if not self.post.get("user_street_number"):
            return {"error": "É necessário informar o número da rua."}
        if not self.post.get("user_complement"):
            return {"error": "É necessário informar um complemento."}

        if not Validation().check_if_cnpj(self.post["user_cnpj"]):
            return {"error": "Digite um CNPJ válido"}
        if not Validation().check_if_number(self.post["user_zip_code"]):
            return {"error": "Digite um ZIP válido"}

        self.user.user_cnpj = self.post["user_cnpj"]
        self.user.user_address_data["user_zip_code"] = self.post["user_zip_code"]
        self.user.user_address_data["user_state"] = self.post["user_state"].upper()
        self.user.user_address_data["user_city"] = self.post["user_city"].title()
        self.user.user_address_data["user_city_code"] = self.post["user_city_code"].capitalize()
        self.user.user_address_data["user_neighborhood"] = self.post["user_neighborhood"].title()
        self.user.user_address_data["user_street"] = self.post["user_street"].title()
        self.user.user_address_data["user_street_number"] = self.post["user_street_number"]
        self.user.user_address_data["user_complement"] = self.post["user_complement"].title()
        self.user.user_client_type = "company"
        self.user_address_data_last_update = str(time.time())
        Dynamo().put_entity(self.user.__dict__)
        return {"success": "Dados atualizados com sucesso"}

    def update_cpf_data(self):
        if not self.post.get("user_cpf"):
            return {"error": "É necessário informar um CPF."}
        if not self.post.get("user_zip_code"):
            return {"error": "É necessário informar um código ZIP."}
        if not self.post.get("user_state"):
            return {"error": "É necessário informar um estado."}
        if not self.post.get("user_city"):
            return {"error": "É necessário informar uma cidade."}
        if not self.post.get("user_city_code"):
            return {"error": "É necessário informar um código de cidade."}
        if not self.post.get("user_neighborhood"):
            return {"error": "É necessário informar um bairro."}
        if not self.post.get("user_street"):
            return {"error": "É necessário informar uma rua."}
        if not self.post.get("user_street_number"):
            return {"error": "É necessário informar o número da rua."}
        if not self.post.get("user_complement"):
            return {"error": "É necessário informar um complemento."}

        if not Validation().check_if_cpf(self.post["user_cpf"]):
            return {"error": "Digite um CPF válido"}
        if not Validation().check_if_number(self.post["user_zip_code"]):
            return {"error": "Digite um ZIP válido"}

        self.user.user_cpf = self.post["user_cpf"]
        self.user.user_address_data["user_zip_code"] = self.post["user_zip_code"]
        self.user.user_address_data["user_state"] = self.post["user_state"].upper()
        self.user.user_address_data["user_city"] = self.post["user_city"].title()
        self.user.user_address_data["user_city_code"] = self.post["user_city_code"].capitalize()
        self.user.user_address_data["user_neighborhood"] = self.post["user_neighborhood"].title()
        self.user.user_address_data["user_street"] = self.post["user_street"].title()
        self.user.user_address_data["user_street_number"] = self.post["user_street_number"]
        self.user.user_address_data["user_complement"] = self.post["user_complement"].title()
        self.user.user_client_type = "physical"
        self.user_address_data_last_update = str(time.time())
        Dynamo().put_entity(self.user.__dict__)
        return {"success": "Dados atualizados com sucesso"}

    def update_personal_data(self):
        if not self.post.get("user_name"):
            return {"error": "É necessário informar um nome."}
        if not self.post.get("user_email"):
            return {"error": "É necessário informar um email."}
        if not self.post.get("user_country"):
            return {"error": "É necessário informar um país."}
        if not self.post.get("user_phone"):
            return {"error": "É necessário informar um telefone."}
        if not " " in self.post.get("user_name"):
            return {"error": "É necessário informar o seu nome completo"}
        if not Validation().check_if_phone(self.post["user_phone"], self.post["user_country"].upper()):
            return {"error": "É necessário um número de telefone válido"}

        if self.post["user_country"] == "BR" and self.user.user_client_type not in ("physical", "company"):
            self.user.user_client_type = "physical"
        if self.post["user_country"] != "BR" and self.user.user_client_type in ("physical", "company"):
            self.user.user_client_type = "international"

        self.user.user_address_data["user_country"] = self.post["user_country"]
        self.user.user_name = self.post["user_name"].title()
        self.user.user_phone = self.post["user_phone"]

        Dynamo().put_entity(self.user.__dict__)
        if self.user.user_email != self.post["user_email"]:
            check_user = load_user(self.post["user_email"])
            if load_user(self.post["user_email"]):
                return {"success": "Perfil atualizado porém o email selecionado para alteração já possui uma conta vinculada"}
            self.user.update_auth_token()
            self.send_email_modified_email(self.user.user_email, self.user.user_auth_token, self.post["user_email"])
            return {"success": "Perfil atualizado porém para alterar o seu email é necessário seguir as instruções que acabamos de enviar para o seu email atual"}

        return {"success": "Dados atualizados com sucesso"}

    def delete_notification(self):
        if not self.post.get("notification_id"):
            return {"error": "Nenhum notification_id informado"}
        notification = Dynamo().get_user_notification(self.user.user_id, self.post["notification_id"])
        if not notification:
            return {"error": "Nenhuma notificação encontrada"}
        Dynamo().delete_entity(notification)
        return {"success": "Notificação excluída"}

    def delete_account(self):
        # if self.user.user_subscription_valid_until and self.user.user_subscription_status and self.user.user_subscription_status != "canceled" and float(self.user.user_subscription_valid_until) > float(time.time()):
        #     return {"error": "Não é possível excluir a conta enquanto tiver uma assinatura que ainda se encontra dentro da data de validade"}
        # if self.user.user_plan_id:
        #     return {"error": "Não é possível excluir a conta enquanto tiver um plano vínculado a sua conta"}

        if self.user.user_stripe_customer_id:
            StripeController().delete_customer(self.user.user_stripe_customer_id)
            self.user.update_attribute("user_stripe_customer_id", "")

        self.user.delete_account()
        return {"success": "Usuário excluído", "redirect_link": lambda_constants["domain_name_url"] + "/user_login/?error_msg=" + EncodeDecode().encode_to_url("Todos os dados da sua conta foram excluídos")}

    def get_user_used_cloud_space_in_mbs(self):
        user_plan = self.user.get_user_actual_plan()
        return {"success": str(round(float(self.user.user_used_cloud_space_in_mbs), 1)), "class": self.generate_progress_class(self.user.user_used_cloud_space_in_mbs, user_plan["plan_cloud_space_in_mbs"])}

    def disconnect_device(self):
        if not self.post.get("device_id"):
            return {"error": "Nenhum device_id informado no formulário."}
        user_device = Dynamo().get_user_device(self.user.user_id, self.post["device_id"])
        if not user_device:
            return {"error": "Este usuário não possui este dispositivo"}

        user_plan = self.user.get_user_actual_plan()
        user_devices = Dynamo().query_all_user_devices(self.user.user_id)
        connected_devices, disconnected_devices = generate_connected_and_disconnected_devices(user_devices)
        disconnected_devices_in_last_30d = generate_disconnected_devices_in_last_30d(disconnected_devices)
        if len(disconnected_devices_in_last_30d) >= int(user_plan["plan_maxium_devices_changes_in_30d"]):
            return {"error": "Este usuário já atingiu o limite máximo de desativações no último mês"}

        disconnect_device(user_device)
        return {"success": "Dispositivo disconectado com sucesso"}

    def add_random_device(self):
        import random
        from utils.Config import devices

        new_device = devices[random.choice(list(devices.keys()))]

        user_device = Dynamo().get_user_device(self.user.user_id, new_device["device_id"])
        if user_device and user_device["device_status"] == "connected":
            return {"error": "Este dispositivo já se encontra conectado"}

        user_plan = self.user.get_user_actual_plan()
        user_devices = Dynamo().query_all_user_devices(self.user.user_id)
        connected_devices, disconnected_devices = generate_connected_and_disconnected_devices(user_devices)

        if len(connected_devices) >= int(user_plan["plan_maxium_devices_available"]):
            return {"error": "Este usuário já atingiu o número máximo de dispositivos conectados"}

        self.user.connect_device(new_device)
        return {"success": "Dispositivo atualizado com sucesso"}

    def update_user_thumb(self):
        if not self.post.get("thumb_key"):
            return {"error": "Nenhuma key de imagem foi recebida"}
        if not S3().check_if_file_exists(lambda_constants["upload_bucket"], self.post["thumb_key"]):
            return {"error": "A o upload da imagem não ocorreu com sucesso"}
        if self.post["thumb_key"].split(".")[-1].lower() not in ["jpg", "jpeg", "png"]:
            return {"error": "É necessário que a imagem seja do tipo JPG/JPEG/PNG"}
        if int(S3().get_filesize(lambda_constants["upload_bucket"], self.post["thumb_key"])) / 1024 / 1024 > 2:
            return {"error": "A imagem excede o tamanho máximo de 2mb"}
        new_image_key = "user_thumbs/" + self.user.user_id + "/" + self.post["thumb_key"]
        S3().copy_file_from_one_bucket_to_another(lambda_constants["upload_bucket"], self.post["thumb_key"], lambda_constants["processed_bucket"], new_image_key)
        self.user.update_attribute("user_thumb", new_image_key)
        return {"success": "Imagem atualizada com sucesso", "user_thumb": new_image_key}

    def remove_coupon_from_user(self):
        self.user.remove_user_cart_coupon_code()
        return {"success": "Cupom removido do usuário"}

    def add_coupon_to_user(self):
        if not self.post.get("coupon_code"):
            return {"error": "Nenhum código de cupom informado"}
        coupon = Dynamo().get_coupon(self.post["coupon_code"])
        if not coupon:
            self.user.remove_user_cart_coupon_code()
            return {"error": "Nenhum cupom encontrado com este código"}
        if self.post["plan_recurrency"] not in ("monthly", "annually"):
            self.user.remove_user_cart_coupon_code()
            return {"error": "Recorrência inválida para se adicionar cupom"}
        if self.post["plan_id"] not in coupon["coupons_plans_ids"]:
            self.user.remove_user_cart_coupon_code()
            return {"error": "Este cupom não está disponível para este plano"}
        if self.post["plan_recurrency"] == "monthly" and not coupon["coupon_available_monthly"]:
            self.user.remove_user_cart_coupon_code()
            return {"error": "Este cupom não está disponível para a recorrência mensal"}
        if self.post["plan_recurrency"] == "annually" and not coupon["coupon_available_annually"]:
            self.user.remove_user_cart_coupon_code()
            return {"error": "Este cupom não está disponível para a recorrência anual"}
        if (self.user.user_cart_currency == "brl" and not coupon["coupon_available_in_brl"]) or (self.user.user_cart_currency == "usd" and not coupon["coupon_available_in_usd"]):
            self.user.remove_user_cart_coupon_code()
            return {"error": "Este cupom não está disponível para a sua localidade"}
        if coupon["coupon_has_limited_uses_count"] and (int(coupon["coupon_actual_uses_count"]) >= int(coupon["coupon_maxium_uses_count"])):
            self.user.remove_user_cart_coupon_code()
            return {"error": "Este cupom já atingiu a quantidade máxima de utilizações disponíveis"}
        if coupon["coupon_available_for_limited_time"] and (int(time.time()) < int(coupon["coupon_start_date"] or int(time.time()) > int(coupon["coupon_end_date"]))):
            self.user.remove_user_cart_coupon_code()
            return {"error": "Este cupom se encontra fora da data de válidade"}
        if self.user.check_if_already_used_coupom(coupon):
            self.user.remove_user_cart_coupon_code()
            return {"error": "Você já utilizou este cupom"}

        self.user.update_attribute("user_cart_coupon_code", coupon["coupon_code"])
        return {"success": "Cupom adicionado"}

    def create_payment_method(self):
        stripe_payment_method = StripeController().get_payment_method(self.post["payment_method_id"])
        if not stripe_payment_method:
            return {"error": "Nenhum método de pagamento encontrado no Stripe com os dados informados"}

        stripe_payment_method = StripeController().attach_payment_method_to_customer(self.user.user_stripe_customer_id, self.post["payment_method_id"])

        payment_method = UserPaymentMethod(self.user.user_id, stripe_payment_method["id"]).__dict__
        payment_method["payment_method_type"] = stripe_payment_method["type"]
        payment_method["payment_method_card"] = {}
        for key, val in stripe_payment_method["card"].items():
            if type(val) == str or type(val) == int:
                payment_method["payment_method_card"][key] = str(val)

        Dynamo().put_entity(payment_method)
        return {"success": "Novo método de pagamento adicionado"}

    def make_default_payment_method(self):
        payment_method = Dynamo().get_payment_method(self.user.user_id, self.post["payment_method_id"])
        if not payment_method:
            return {"error": "Nenhum método de pagamento encontrado com os dados informados"}
        user_subscription = Dynamo().get_subscription(self.user.user_subscription_id)
        if not user_subscription:
            return {"error": "Você não possui uma assinatura para trocar o método de pagamento"}
        if payment_method["payment_method_type"] != "card" and user_subscription["subscription_recurrency"] == "monthly":
            return {"error": "Não é possível trocar o método de pagamento em uma assinatura mensal para um método diferente de cartão"}
        if user_subscription["subscription_is_trial"]:
            return {"error": "Não é possível trocar o método de pagamento de uma assinatura trial"}
        if user_subscription["subscription_status"] != "active":
            return {"error": "Não é possível trocar o método de pagamento de uma assinatura que não está ativa"}
        if user_subscription.get("subscription_default_payment_method") == payment_method["payment_method_id"]:
            return {"success": "Não é possível tornar padrão um método de pagamento que já é o padrão"}
        StripeController().update_subscription_payment_method(user_subscription["subscription_id"], payment_method["payment_method_id"])
        user_subscription["subscription_default_payment_method"] = payment_method["payment_method_id"]
        Dynamo().update_entity(user_subscription, "subscription_default_payment_method", user_subscription["subscription_default_payment_method"])
        return {"success": "Método de pagamento da assinatura atual alterado"}

    def delete_payment_method(self):
        payment_method = Dynamo().get_payment_method(self.user.user_id, self.post["payment_method_id"])
        if not payment_method:
            return {"error": "Nenhum método de pagamento encontrado com os dados informados"}
        user_subscription = Dynamo().get_subscription(self.user.user_subscription_id)
        if user_subscription.get("subscription_default_payment_method") == payment_method["payment_method_id"]:
            return {"error": "Não é possível excluir o método de pagamento padrão da sua assinatura"}

        StripeController().delete_payment_method(payment_method["payment_method_id"])
        Dynamo().delete_entity(payment_method)
        return {"success": "Método de pagamento deletado"}

    def update_user_pagination_count(self):
        self.user.update_attribute("user_pagination_count", self.post["user_pagination_count"])
        return {"success": "Tamanho de página de usuário atualizado"}

    def cancel_user_current_subscription(self):
        if not self.user.user_subscription_id:
            return {"error": "O usuário não possui nenhuma subscription_id"}
        user_subscription = Dynamo().get_subscription(self.user.user_subscription_id)
        if not user_subscription:
            return {"error": "Assinatura não encontrada"}
        if user_subscription["subscription_status"] != "active":
            return {"error": "A assinatura não se encontra ativa"}
        self.user.cancel_current_subscription()
        canceled_subscription = CancelSubscription(user_subscription["subscription_id"], self.user.user_id).__dict__
        canceled_subscription["cancel_subscription_found_a_better"] = self.post["cancel_subscription_found_a_better"]
        canceled_subscription["cancel_subscription_unhappy_service"] = self.post["cancel_subscription_unhappy_service"]
        canceled_subscription["cancel_subscription_technical_problems"] = self.post["cancel_subscription_technical_problems"]
        canceled_subscription["cancel_subscription_too_expensive"] = self.post["cancel_subscription_too_expensive"]
        canceled_subscription["cancel_subscription_not_using"] = self.post["cancel_subscription_not_using"]
        canceled_subscription["cancel_subscription_other_reasons"] = self.post["cancel_subscription_other_reasons"]
        canceled_subscription["cancel_subscription_text_area"] = self.post.get("cancel_subscription_text_area", "")
        Dynamo().put_entity(canceled_subscription)
        increase_backoffice_data_total_count("cancel_subscription")
        return {"success": "Assinatura cancelada"}

    def check_if_user_can_upgrade_his_plan(self):
        plan = Dynamo().get_plan(self.post["plan_id"])
        if not plan:
            return {"error": "Nenhum plano encontrado com este plan_id", "user_client_type": self.user.user_client_type}
        if not self.user.check_if_payment_ready():
            return {"error": "É necessário atualizar os seus dados para processeguir na compra", "user_client_type": self.user.user_client_type}
        if float(self.user.user_address_data_last_update) < float(time.time() - 3600):
            return {"error": "É necessário confirmar os seus dados para processeguir na compra", "user_client_type": self.user.user_client_type}
        else:
            return {"success": "O usuário pode trocar o seu plano atual"}

    def remove_folder_from_shared(self):
        self.user.remove_folder_from_user_shared_dicts(self.post["folder_id"])
        return {"success": "Pasta removida dos compartilhamentos"}

    def update_folder_is_acessible(self):
        folder = Dynamo().get_folder(self.post["folder_id"])
        if not folder:
            return {"error": "Nenhuma pasta encontrada com os dados fornecidos"}
        if folder["folder_user_id"] != self.user.user_id:
            return {"error": "Esta pasta não pertence a este usuário"}

        folder["folder_is_accessible"] = self.post.get("folder_is_accessible")
        Dynamo().put_entity(folder)
        return {"success": "Acessibilidade da pasta atualizada"}

    def update_folder_password(self):
        folder = Dynamo().get_folder(self.post["folder_id"])
        if not folder:
            return {"error": "Nenhuma pasta encontrada com os dados fornecidos"}
        if folder["folder_user_id"] != self.user.user_id:
            return {"error": "Esta pasta não pertence a este usuário"}

        folder_is_accessible = self.post.get("folder_is_accessible")
        folder_is_password_protected = self.post.get("folder_is_password_protected")
        folder_password = self.post.get("folder_password")

        folder["folder_is_accessible"] = folder_is_accessible
        if folder_is_accessible and folder_is_password_protected and not folder_password:
            return {"error": "É necessário informar uma senha"}
        folder["folder_password"] = folder_password if folder_password else ""
        folder["folder_is_password_protected"] = folder_is_password_protected

        Dynamo().put_entity(folder)
        return {"success": "Senha da pasta atualizada"}

    def remove_model_from_shared(self):
        model = Dynamo().get_model(self.post["model_id"])
        if not model:
            return {"error": "Nenhum projeto encontrado com os dados fornecidos"}
        self.user.remove_model_from_user_dicts(model, shared=True)
        return {"success": "Projeto removido dos compartilhados"}

    def add_model_to_user_favorites(self):
        if self.post["model_is_favorite"] == "False":
            self.user.remove_model_id_from_favorites(self.post["model_id"])
        else:
            self.user.add_model_id_to_favorites(self.post["model_id"])
        return {"success": "Favoritos do usuário atualizados"}

    def add_folder_to_user_favorites(self):
        if self.post["folder_is_favorite"] == "False":
            self.user.remove_folder_id_from_favorites(self.post["folder_id"])
        else:
            self.user.add_folder_id_to_favorites(self.post["folder_id"])
        return {"success": "Favoritos do usuário atualizados"}

    def add_shared(self):
        if not self.post.get("shared_link"):
            return {"error": "Informe um link para adicionar o arquivo à sua conta"}
        if "model_code" in self.post["shared_link"]:
            model = Dynamo().get_model_by_code(self.post["shared_link"].split("model_code=")[1])
            if not model:
                return {"error": "Nenhum projeto encontrado com o link fornecido"}
            if not model["model_is_accessible"]:
                return {"error": "Este projeto não se encontra acessível através de compartilhamento"}
            if model["model_is_password_protected"] and not self.post.get("shared_password"):
                return {"error": "É necessário informar uma senha para acessar este arquivo", "command": "open_password_modal"}
            if model["model_is_password_protected"] and (model["model_password"] != self.post.get("shared_password")):
                return {"error": "A senha informada está incorreta"}

            if self.user:
                if model["model_user_id"] == self.user.user_id:
                    return {"error": "Este modelo já pertence a este usuário"}
                user_shared_dicts = Dynamo().get_folder(self.user.user_shared_dicts_folder_id)
                if model["model_id"] not in user_shared_dicts["files"]:
                    self.user.add_model_to_user_dicts(model, shared=True)

            create_notification_model_shared_with_me(self.user.user_id, model["model_name"])
            return {"success": "Modelo adicionado aos compartilhados"}

        else:
            folder_id = self.post["shared_link"]
            if "folder_id=" in self.post["shared_link"]:
                folder_id = self.post["shared_link"].split("folder_id=")[1]
            folder = Dynamo().get_folder(folder_id)
            if not folder:
                return {"error": "Nenhuma pasta encontrada com o link fornecido"}
            if not folder["folder_is_accessible"]:
                return {"error": "Esta pasta não se encontra acessível através de compartilhamento"}

            if folder["folder_is_password_protected"] and not self.post.get("shared_password"):
                return {"error": "É necessário informar uma senha para acessar este arquivo", "command": "open_password_modal"}
            if folder["folder_is_password_protected"] and (folder["folder_password"] != self.post.get("shared_password")):
                return {"error": "A senha informada está incorreta"}

            if self.user:
                if folder["folder_user_id"] == self.user.user_id:
                    return {"error": "Esta pasta já pertence a este usuário"}
                user_shared_dicts = Dynamo().get_folder(self.user.user_shared_dicts_folder_id)
                if folder["folder_id"] not in user_shared_dicts["folders"]:
                    self.user.add_folder_to_user_shared_dicts(user_shared_dicts, folder)
            return {"success": "Pasta adicionada aos compartilhados", "has_user": bool(self.user), "folder_id": folder_id}

    def create_folder(self):
        if not self.post.get("folder_name"):
            return {"error": "É necessário informar um nome para o novo diretório"}

        self.user.create_new_folder(self.post["folder_name"], self.post.get("folder_id"))
        return {"success": "Usuário atualizado"}

    def download_folder(self):
        download_links = []
        folder = Dynamo().get_folder(self.post["folder_id"])
        if not folder:
            return {"error": "Nenhuma pasta"}
        if folder["folder_user_id"] != self.user.user_id:
            return {"error": "Esta pasta não pertence a este usuária"}

        if folder:
            if float(folder["folder_size_in_mbs"]) < 10000:
                lambda_generate_folder_zip_reponse = Lambda().invoke(lambda_constants["lambda_generate_folder_zip"], "RequestResponse", {"folder_id": self.post["folder_id"]})
                download_links.append({"model_save_name": folder["folder_name"] + ".zip", "model_link": lambda_generate_folder_zip_reponse["success"]})
            else:
                if folder["files"]:
                    for model_id in folder["files"]:
                        model = Dynamo().get_model(model_id)
                        if model:
                            download_links.append({"model_save_name": model["model_name"] + ".zip", "model_link": ModelController().generate_model_download_link(model)})
            return {"success": "Links gerados", "download_links": download_links}
        return {"error": "Nenhuma pasta"}

    def download_model(self):
        download_links = []
        model = Dynamo().get_model(self.post["model_id"])
        if not model:
            return {"error": "Nenhum modelo"}
        if model["model_user_id"] != self.user.user_id:
            return {"error": "Este modelo não pertence a este usuário"}

        if model:
            # if int(int(model["model_filesize"]) / 1024 / 1024) < 10000:
            if model["model_federated_required_ids"]:
                lambda_generate_folder_zip_reponse = Lambda().invoke(lambda_constants["lambda_generate_folder_zip"], "RequestResponse", {"model_id": self.post["model_id"]})
                download_links.append({"model_save_name": model["model_name"] + ".zip", "model_link": lambda_generate_folder_zip_reponse["success"]})
            else:
                download_links.append({"model_save_name": model["model_name"] + ".zip", "model_link": ModelController().generate_model_download_link(model)})
            return {"success": "Links gerados", "download_links": download_links}
        return {"error": "Nenhuma pasta"}

    def get_folder(self):
        folder = Dynamo().get_folder(self.post["folder_id"])
        if folder:
            return {"success": "Folder encontrado", "folder": folder}
        return {"error": "Nenhuma pasta"}

    def get_root_folder(self):
        if not self.post.get("folder_id"):
            return {"error": "Nenhum folder_id no post"}
        folder = Dynamo().get_folder(self.post["folder_id"])
        root_folder = Dynamo().get_folder(folder["folder_root_id"])
        if root_folder:
            return {"success": "Folder encontrado", "root_folder": root_folder}
        return {"error": "Sem root folder"}

    def delete_folder(self):
        folder = Dynamo().get_folder(self.post["folder_id"])
        if folder["folder_user_id"] != self.user.user_id:
            return {"error": "Esta pasta não pertence a este usuário"}

        self.user.delete_folder(folder)
        return {"success": "Folder deletado"}

    def rename_folder(self):
        folder = Dynamo().get_folder(self.post["folder_id"])
        if folder["folder_user_id"] != self.user.user_id:
            return {"error": "Esta pasta não pertence a este usuário"}
        if "/" in self.post["folder_new_name"]:
            return {"error": "O nome da pasta não pode conter barras '/'."}

        folder["folder_path"] = folder["folder_path"].replace(folder["folder_name"], self.post["folder_new_name"].strip())
        folder["folder_name"] = self.post["folder_new_name"].strip()
        Dynamo().put_entity(folder)
        return {"success": "Folder renomeado"}

    def move_model_folder(self):
        model = Dynamo().get_model(self.post["model_id"])
        if self.post.get("selected_folder_id"):
            folder = Dynamo().get_folder(self.post["selected_folder_id"])
            if folder["folder_user_id"] != self.user.user_id:
                return {"error": "Esta pasta não pertence a este usuário"}
            if model["model_folder_id"] == folder["folder_id"]:
                return {"error": "Este arquivo já se encontra neste diretório"}
            self.user.move_model_to_another_folder(model, folder)
        else:
            self.user.move_model_to_another_folder(model)
        return {"success": "Modelo movido"}

    def move_folder_to_another_folder(self):
        folder = Dynamo().get_folder(self.post["folder_id"])

        if not folder:
            return {"error": "Pasta de origem não encontrada"}
        if folder["folder_user_id"] != self.user.user_id:
            return {"error": "Pasta de origem não pertence a este usuário"}

        selected_folder = ""
        if self.post.get("selected_folder_id"):
            selected_folder = Dynamo().get_folder(self.post["selected_folder_id"])
            if selected_folder:
                if selected_folder["folder_user_id"] != self.user.user_id:
                    return {"error": "Pasta de destino não pertence a este usuário"}
                if not check_if_folder_movement_is_valid(folder, selected_folder):
                    return {"error": "Não é possível mover uma pasta para dentro dela própria"}

        self.user.move_folder_to_another_folder(folder, selected_folder)
        return {"success": "Folder movido para outro folder"}
