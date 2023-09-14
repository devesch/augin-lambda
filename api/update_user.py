import json
from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.controllers.project_controller import ProjectController
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Lambda import Lambda
from utils.Config import lambda_constants
from objects.UserFolder import check_if_folder_movement_is_valid


class UpdateUser(BasePage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "no command in post"}

        if self.post["command"] == "remove_folder_from_shared":
            self.user.remove_folder_from_user_shared_dicts(self.post["folder_id"])
            return {"success": "folder removed from shared"}

        if self.post["command"] == "update_folder_password":
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
                return {"error": "É necessário informar uma senha."}
            folder["folder_password"] = folder_password if folder_password else ""
            folder["folder_is_password_protected"] = folder_is_password_protected

            Dynamo().put_entity(folder)
            return {"success": "folder password updated"}

        if self.post["command"] == "remove_model_from_shared":
            model = Dynamo().get_model(self.post["model_id"])
            if not model:
                return {"error": "Nenhum projeto encontrado com os dados fornecidos"}
            self.user.remove_model_from_user_dicts(model, shared=True)
            return {"success": "Projeto removido dos compartilhados"}

        if self.post["command"] == "add_model_to_user_favorites":
            if self.post["model_is_favorite"] == "False":
                self.user.remove_model_id_from_favorites(self.post["model_id"])
            else:
                self.user.add_model_id_to_favorites(self.post["model_id"])
            return {"success": "user favorites updated"}

        if self.post["command"] == "add_folder_to_user_favorites":
            if self.post["folder_is_favorite"] == "False":
                self.user.remove_folder_id_from_favorites(self.post["folder_id"])
            else:
                self.user.add_folder_id_to_favorites(self.post["folder_id"])
            return {"success": "user favorites updated"}

        if self.post["command"] == "add_shared":
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

        if self.post["command"] == "create_folder":
            if not self.post.get("folder_name"):
                return {"error": "É necessário informar um nome para o novo diretório."}

            self.user.create_new_folder(self.post["folder_name"], self.post.get("folder_id"))
            return {"success": "User updated."}

        elif self.post["command"] == "download_folder":
            download_links = []
            folder = Dynamo().get_folder(self.post["folder_id"])
            if not folder:
                return {"error": "no folder"}
            if folder["folder_user_id"] != self.user.user_id:
                return {"error": "this folder doesnt belong to user"}

            if folder:
                if int(folder["folder_size_in_mbs"]) < 10000:
                    lambda_generate_folder_zip_reponse = Lambda().invoke(lambda_constants["lambda_generate_folder_zip"], "RequestResponse", {"folder_id": self.post["folder_id"]})
                    download_links.append({"model_save_name": folder["folder_name"] + ".zip", "model_link": lambda_generate_folder_zip_reponse["success"]})
                else:
                    if folder["files"]:
                        for model_id in folder["files"]:
                            model = Dynamo().get_model(model_id)
                            if model:
                                download_links.append({"model_save_name": model["model_name"] + ".zip", "model_link": ModelController().generate_model_download_link(model)})
                return {"success": download_links}

            return {"error": "no folder"}

        elif self.post["command"] == "download_model":
            download_links = []
            model = Dynamo().get_model(self.post["model_id"])
            if not model:
                return {"error": "no model"}
            if model["model_user_id"] != self.user.user_id:
                return {"error": "this model doesnt belong to user"}

            if model:
                # if int(int(model["model_filesize"]) / 1024 / 1024) < 10000:
                if model["model_federated_required_ids"]:
                    lambda_generate_folder_zip_reponse = Lambda().invoke(lambda_constants["lambda_generate_folder_zip"], "RequestResponse", {"model_id": self.post["model_id"]})
                    download_links.append({"model_save_name": model["model_name"] + ".zip", "model_link": lambda_generate_folder_zip_reponse["success"]})
                else:
                    download_links.append({"model_save_name": model["model_name"] + ".zip", "model_link": ModelController().generate_model_download_link(model)})
                return {"success": download_links}

            return {"error": "no folder"}

        elif self.post["command"] == "get_folder":
            folder = Dynamo().get_folder(self.post["folder_id"])
            if folder:
                return {"success": folder}

            return {"error": "no folder"}

        elif self.post["command"] == "get_root_folder":
            if not self.post.get("folder_id"):
                return {"error": "no folder_id in post"}
            folder = Dynamo().get_folder(self.post["folder_id"])
            root_folder = Dynamo().get_folder(folder["folder_root_id"])
            if root_folder:
                return {"success": root_folder}

            return {"error": "no root folder"}

        elif self.post["command"] == "delete_folder":
            folder = Dynamo().get_folder(self.post["folder_id"])
            if folder["folder_user_id"] != self.user.user_id:
                return {"error": "Esta pasta não pertence a este usuário."}

            self.user.delete_folder(folder)
            return {"success": "folder deleted"}

        elif self.post["command"] == "rename_folder":
            folder = Dynamo().get_folder(self.post["folder_id"])
            if folder["folder_user_id"] != self.user.user_id:
                return {"error": "Esta pasta não pertence a este usuário."}
            if "/" in self.post["folder_new_name"]:
                return {"error": "O nome da pasta não pode conter barras '/'."}

            folder["folder_path"] = folder["folder_path"].replace(folder["folder_name"], self.post["folder_new_name"].strip())
            folder["folder_name"] = self.post["folder_new_name"].strip()
            Dynamo().put_entity(folder)
            return {"success": "folder renamed"}

        elif self.post["command"] == "move_model_folder":
            model = Dynamo().get_model(self.post["model_id"])
            if self.post.get("selected_folder_id"):
                folder = Dynamo().get_folder(self.post["selected_folder_id"])
                if folder["folder_user_id"] != self.user.user_id:
                    return {"error": "Esta pasta não pertence a este usuário."}
                self.user.move_model_to_another_folder(model, folder)
            else:
                self.user.move_model_to_another_folder(model)

            return {"success": "model moved"}

        elif self.post["command"] == "move_folder_to_another_folder":
            folder = Dynamo().get_folder(self.post["folder_id"])

            if not folder:
                return {"error": "Pasta de origem não encontrada."}
            if folder["folder_user_id"] != self.user.user_id:
                return {"error": "Pasta de origem não pertence a este usuário."}

            selected_folder = ""
            if self.post.get("selected_folder_id"):
                selected_folder = Dynamo().get_folder(self.post["selected_folder_id"])
                if selected_folder:
                    if selected_folder["folder_user_id"] != self.user.user_id:
                        return {"error": "Pasta de destino não pertence a este usuário."}
                    if not check_if_folder_movement_is_valid(folder, selected_folder):
                        return {"error": "Não é possível mover uma pasta para dentro dela própria."}

            self.user.move_folder_to_another_folder(folder, selected_folder)
            return {"success": "folder moved to another folder"}

        return {"error": "no valid command in post"}
