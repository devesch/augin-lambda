from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.controllers.project_controller import ProjectController
from python_web_frame.controllers.stripe_controller import StripeController
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Lambda import Lambda
from utils.AWS.S3 import S3
from utils.Config import lambda_constants
from objects.UserFolder import check_if_folder_movement_is_valid
from objects.UserPaymentMethod import UserPaymentMethod


class UpdateUser(BasePage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "Nenhum command no post"}

        if self.post["command"] not in ("get_root_folder", "add_shared"):
            if not self.user:
                return {"error": "Nenhum usuário encontrado"}

        return getattr(self, self.post["command"])()

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
        self.user.update_user_attribute(self, "user_thumb", new_image_key)
        return {"success": "Imagem atualizada com sucesso", "user_thumb": new_image_key}

    def add_coupon_to_user(self):
        import time

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

        self.user.update_user_attribute("user_cart_coupon_code", coupon["coupon_code"])
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
        self.user.update_user_attribute("user_pagination_count", self.post["user_pagination_count"])
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
        return {"success": "Assinatura cancelada"}

    def check_if_user_can_upgrade_his_plan(self):
        plan = Dynamo().get_plan(self.post["plan_id"])
        if not plan:
            return {"error": "Nenhum plano encontrado com este plan_id", "user_client_type": self.user.user_client_type}
        if not self.user.check_if_is_payment_ready():
            return {"error": "É necessário que o usuário atualize os seus dados", "user_client_type": self.user.user_client_type}
        else:
            return {"success": "O usuário pode trocar o seu plano atual"}

    def remove_folder_from_shared(self):
        self.user.remove_folder_from_user_shared_dicts(self.post["folder_id"])
        return {"success": "folder removed from shared"}

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
        return {"success": "folder password updated"}

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
        return {"success": "user favorites updated"}

    def add_folder_to_user_favorites(self):
        if self.post["folder_is_favorite"] == "False":
            self.user.remove_folder_id_from_favorites(self.post["folder_id"])
        else:
            self.user.add_folder_id_to_favorites(self.post["folder_id"])
        return {"success": "user favorites updated"}

    def add_shared(self):
        ### TODO BEFORE PROD: NOT LET USER ADD HIS OWN FOLDERS AND FILES TO SHARED
        if not self.post.get("shared_link"):
            return {"error": "Informe um link para adicionar o arquivo à sua conta"}
        if "model_code" in self.post["shared_link"]:
            model = Dynamo().get_model_by_code(self.post["shared_link"].split("model_code=")[1])
            if not model:
                return {"error": "Nenhum projeto encontrado com o link fornecido"}
            if not model["model_is_accessible"]:
                return {"error": "Este projeto não se encontra acessível através de compartilhamento"}
            user_shared_dicts = Dynamo().get_folder(self.user.user_shared_dicts_folder_id)
            if model["model_id"] in user_shared_dicts:
                return {"error": "Este modelo já se encontra nos seus compartilhados"}
            if model["model_is_password_protected"] and not self.post.get("shared_password"):
                return {"error": "É necessário informar uma senha para acessar este arquivo", "command": "open_password_modal"}
            if model["model_is_password_protected"] and (model["model_password"] != self.post.get("shared_password")):
                return {"error": "A senha informada está incorreta"}
            self.user.add_model_to_user_dicts(model, shared=True)
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
                user_shared_dicts = Dynamo().get_folder(self.user.user_shared_dicts_folder_id)
                if folder["folder_id"] not in user_shared_dicts["folders"]:
                    self.user.add_folder_to_user_shared_dicts(user_shared_dicts, folder)
            return {"success": "Pasta adicionada aos compartilhados", "has_user": bool(self.user), "folder_id": folder_id}

    def create_folder(self):
        if not self.post.get("folder_name"):
            return {"error": "É necessário informar um nome para o novo diretório"}

        self.user.create_new_folder(self.post["folder_name"], self.post.get("folder_id"))
        return {"success": "User updated."}

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
            return {"success": download_links}
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
            return {"success": download_links}
        return {"error": "Nenhuma pasta"}

    def get_folder(self):
        folder = Dynamo().get_folder(self.post["folder_id"])
        if folder:
            return {"success": folder}
        return {"error": "Nenhuma pasta"}

    def get_root_folder(self):
        if not self.post.get("folder_id"):
            return {"error": "Nenhum folder_id no post"}
        folder = Dynamo().get_folder(self.post["folder_id"])
        root_folder = Dynamo().get_folder(folder["folder_root_id"])
        if root_folder:
            return {"success": root_folder}
        return {"error": "Sem root folder"}

    def delete_folder(self):
        folder = Dynamo().get_folder(self.post["folder_id"])
        if folder["folder_user_id"] != self.user.user_id:
            return {"error": "Esta pasta não pertence a este usuário"}

        self.user.delete_folder(folder)
        return {"success": "folder deleted"}

    def rename_folder(self):
        folder = Dynamo().get_folder(self.post["folder_id"])
        if folder["folder_user_id"] != self.user.user_id:
            return {"error": "Esta pasta não pertence a este usuário"}
        if "/" in self.post["folder_new_name"]:
            return {"error": "O nome da pasta não pode conter barras '/'."}

        folder["folder_path"] = folder["folder_path"].replace(folder["folder_name"], self.post["folder_new_name"].strip())
        folder["folder_name"] = self.post["folder_new_name"].strip()
        Dynamo().put_entity(folder)
        return {"success": "folder renamed"}

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
        return {"success": "model moved"}

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
        return {"success": "folder moved to another folder"}
