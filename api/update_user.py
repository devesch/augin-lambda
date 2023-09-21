from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.controllers.project_controller import ProjectController
from python_web_frame.controllers.stripe_controller import StripeController
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Lambda import Lambda
from utils.Config import lambda_constants
from objects.UserFolder import check_if_folder_movement_is_valid


class UpdateUser(BasePage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "Nenhum command no post"}
        if not self.user:
            return {"error": "Nenhum usuário encontrado"}

        return getattr(self, self.post["command"])()

    def cancel_user_current_subscription(self):
        if not self.user.user_subscription_id:
            return {"error": "O usuário não possui nenhuma subscription_id"}
        user_subscription = Dynamo().get_subscription(self.user.user_subscription_id)
        if not user_subscription:
            return {"error": "Assinatura não encontrada"}
        if user_subscription["subscription_status"] != "active":
            return {"error": "A assinatura não se encontra ativa"}
        StripeController().cancel_subscription(self.user.user_subscription_id)
        stripe_subscription = StripeController().get_subscription(self.user.user_subscription_id)
        user_subscription["subscription_status"] = stripe_subscription["status"]
        Dynamo().put_entity(user_subscription)
        self.user.change_user_subscription_status(stripe_subscription["status"])
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
        if not "model_id" in self.post["shared_link"] and not "folder_id" in self.post["shared_link"]:
            return {"error": "Nenhum arquivo encontrado com o link fornecido"}
        if "model_id" in self.post["shared_link"]:
            model = Dynamo().get_model(self.post["shared_link"].split("model_id=")[1])
            if not model:
                return {"error": "Nenhum projeto encontrado com o link fornecido"}
            if not model["model_is_accessible"]:
                return {"error": "Este projeto não se encontra acessível através de compartilhamento"}
            if model["model_id"] in self.user.user_shared_dicts["files"]:
                return {"error": "Este modelo já se encontra nos seus compartilhados"}
            if model["model_is_password_protected"] and not self.post.get("shared_password"):
                return {"error": "É necessário informar uma senha para acessar este arquivo", "command": "open_password_modal"}
            if model["model_is_password_protected"] and (model["model_password"] != self.post.get("shared_password")):
                return {"error": "A senha informada está incorreta"}
            self.user.add_model_to_user_dicts(model, shared=True)
            return {"success": "Modelo adicionado aos compartilhados"}
        if "folder_id" in self.post["shared_link"]:
            folder = Dynamo().get_folder(self.post["shared_link"].split("folder_id=")[1])
            if not folder:
                return {"error": "Nenhuma pasta encontrada com o link fornecido"}
            if not folder["folder_is_accessible"]:
                return {"error": "Esta pasta não se encontra acessível através de compartilhamento"}
            if folder["folder_id"] in self.user.user_shared_dicts["folders"]:
                return {"error": "Esta pasta já se encontra nos seus compartilhados"}
            if folder["folder_is_password_protected"] and not self.post.get("shared_password"):
                return {"error": "É necessário informar uma senha para acessar este arquivo", "command": "open_password_modal"}
            if folder["folder_is_password_protected"] and (folder["folder_password"] != self.post.get("shared_password")):
                return {"error": "A senha informada está incorreta"}
            self.user.add_folder_to_user_shared_dicts(folder)
            return {"success": "Pasta adicionada aos compartilhados"}

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
