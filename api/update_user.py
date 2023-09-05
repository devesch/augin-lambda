from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.controllers.project_controller import ProjectController
from utils.AWS.Dynamo import Dynamo
from utils.Config import lambda_constants


class UpdateUser(BasePage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "no command in post"}

        if self.post.get("command"):
            if self.post["command"] == "create_folder":
                if not self.post.get("folder_name"):
                    return {"error": "É necessário informar um nome para o novo diretório."}

                self.user.create_new_folder(self.post["folder_name"], self.post.get("folder_id"))
                return {"success": "User updated."}

            elif self.post["command"] == "get_folder":
                folder = Dynamo().get_folder(self.post["folder_id"])
                if folder:
                    return {"success": folder}

                return {"error": "no folder"}

            elif self.post["command"] == "get_root_folder":
                folder = Dynamo().get_folder(self.post["folder_id"])
                root_folder = Dynamo().get_folder(folder["folder_root_id"])
                if root_folder:
                    return {"success": root_folder}

                return {"error": "no root folder"}

            elif self.post["command"] == "delete_folder":
                folder = Dynamo().get_folder(self.post["folder_id"])
                if folder["folder_user_email"] != self.user.user_email:
                    return {"error": "Esta pasta não pertence a este usuário."}
                if folder["folders"]:
                    return {"error": "Não é possível deletar uma pasta contendo pastas."}
                if folder["files"]:
                    return {"error": "Não é possível deletar uma pasta contendo arquivos."}

                self.user.delete_folder(folder)
                return {"success": "folder deleted"}

            elif self.post["command"] == "rename_folder":
                folder = Dynamo().get_folder(self.post["folder_id"])
                if folder["folder_user_email"] != self.user.user_email:
                    return {"error": "Esta pasta não pertence a este usuário."}
                if "/" in self.post["folder_new_name"]:
                    return {"error": "O nome da pasta não pode conter barras '/'."}

                folder["folder_path"] = folder["folder_path"].replace(folder["folder_name"], self.post["folder_new_name"].strip())
                folder["folder_name"] = self.post["folder_new_name"].strip()
                Dynamo().put_entity(folder)
                return {"success": "folder renamed"}

            elif self.post["command"] == "update_folder_favorite":
                folder = Dynamo().get_folder(self.post["folder_id"])
                if folder["folder_user_email"] != self.user.user_email:
                    return {"error": "Esta pasta não pertence a este usuário."}

                if self.post["folder_is_favorite"] == "True":
                    folder["folder_is_favorite"] = True
                else:
                    folder["folder_is_favorite"] = False
                Dynamo().put_entity(folder)

                return {"success": "folder updated"}

            elif self.post["command"] == "move_model_folder":
                model = Dynamo().get_model_by_id(self.post["model_id"])
                if model["model_user_email"] != self.user.user_email:
                    return {"error": "Este modelo não pertence a este usuário."}
                if self.post.get("selected_folder_id"):
                    folder = Dynamo().get_folder(self.post["selected_folder_id"])
                    if folder["folder_user_email"] != self.user.user_email:
                        return {"error": "Esta pasta não pertence a este usuário."}
                    self.user.move_model_to_another_folder(model, folder)
                else:
                    self.user.move_model_to_another_folder(model)

                return {"success": "model moved"}

        return {"error": "no valid command in post"}
