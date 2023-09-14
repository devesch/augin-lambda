from python_web_frame.base_page import BasePage
from utils.Config import lambda_constants
from utils.utils.Sort import Sort
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Generate import Generate
from utils.AWS.Dynamo import Dynamo
from utils.AWS.S3 import S3
from python_web_frame.controllers.model_controller import ModelController
from objects.User import sort_user_folders


class PanelPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

    def list_html_models_in_processing(self, event, models_in_processing):
        full_html = []
        if models_in_processing:
            models_in_processing = Sort().sort_dict_list(models_in_processing, "created_at", reverse=True, integer=True)
            for model in models_in_processing:
                if ModelController().check_if_model_in_processing_is_with_error(model["created_at"]):
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_models_in_processing_with_error")
                else:
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_models_in_processing")
                if "dev" in event.get_prefix():
                    html.esc("model_was_processed_where_val", model["model_was_processed_where"])
                html.esc("model_id_val", model["model_id"])
                html.esc("model_filename_val", model["model_filename"])
                html.esc("model_processing_percentage_val", model["model_processing_percentage"])
                full_html.append(str(html))
        return "".join(full_html)

    def show_html_uploading_models(self, model_filename, index):
        html = ReadWrite().read_html("panel_create_project/_codes/html_uploading_models")
        html.esc("model_filename_val", model_filename)
        html.esc("index_val", index)
        return str(html)

    def list_html_user_folder_rows(self, folder_id=None, model_html=""):
        full_html = []
        shared = False
        user_ids_name_dict = {self.user.user_id: self.user.user_name}

        if self.route == "panel_shared_project" or self.post.get("page") == "panel_shared_project":
            shared = True

        if self.post.get("model_id_to_be_updated"):
            model_to_be_updated = Dynamo().get_model(self.post.get("model_id_to_be_updated"))

        if not self.post.get("explore_input_search"):
            user_folder = self.user.generate_folder_data(folder_id, shared)
            if user_folder["folders"]:

                for folder in user_folder["folders"]:
                    if folder["folder_user_id"] not in user_ids_name_dict:
                        owner_user = Dynamo().get_user(Dynamo().get_user_email_with_id(folder["folder_user_id"]))
                        user_ids_name_dict[folder["folder_user_id"]] = owner_user["user_name"]
                    folder["owners_name"] = user_ids_name_dict[folder["folder_user_id"]]

                user_folder["folders"] = sort_user_folders(self.user, user_folder["folders"], self.post.get("sort_attribute"), self.post.get("sort_reverse"))
                for folder in user_folder["folders"]:
                    if not model_html:
                        if shared:
                            if not folder["folder_is_accessible"] and not self.post.get("folder_id"):
                                continue
                            html = ReadWrite().read_html("panel_shared_project/_codes/html_user_folder_rows_folders")
                        else:
                            html = ReadWrite().read_html("panel_explore_project/_codes/html_user_folder_rows_folders")
                    elif model_html == "update":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_update_model_user_folder_rows_folders")
                    elif model_html == "move":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_move_model_user_folder_rows_folders")
                    elif model_html == "move_folder":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_move_folder_model_user_folder_rows_folders")
                    elif model_html == "create_federated":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_create_federated_model_user_folder_rows_folders")

                    if shared and self.post.get("folder_id"):
                        html.esc("remove_folder_visibility_val", "display:none;")

                    html.esc("folder_path_val", folder["folder_path"])
                    html.esc("folder_name_val", folder["folder_name"])
                    html.esc("folder_id_val", folder["folder_id"])
                    html.esc("folder_created_at_val", ModelController().convert_model_created_at_to_date(folder["created_at"]))
                    html.esc("folder_size_in_mbs_val", f'{round(float(folder["folder_size_in_mbs"]), 2):.1f}' + " Mb")

                    html.esc("owners_name_val", folder["owners_name"])

                    html.esc("folder_password_val", folder["folder_password"])
                    html.esc("folder_is_accessible_val", folder["folder_is_accessible"])
                    html.esc("folder_share_link_val", folder["folder_share_link"])
                    html.esc("folder_share_link_qrcode_val", folder["folder_share_link_qrcode"])
                    html.esc("folder_is_password_protected_val", folder["folder_is_password_protected"])

                    if not folder["folders"] and not folder["files"]:
                        html.esc("download_folder_visibility_val", "display:none;")

                    if folder["folder_id"] in self.user.user_favorited_folders:
                        html.esc("html_folder_is_favorite", self.show_html_model_is_favorite())
                        html.esc("opposite_folder_is_favorite_val", False)
                        html.esc("favorite_or_unfavorite_val", self.translate("Desfavoritar"))
                        html.esc("favorite_icon_val", "star")
                    else:
                        html.esc("opposite_folder_is_favorite_val", True)
                        html.esc("favorite_or_unfavorite_val", self.translate("Favoritar"))
                        html.esc("favorite_icon_val", "star_black")

                    full_html.append(str(html))

        models = []
        if self.post.get("explore_input_search"):
            models = ModelController().search_models_by_name(self.post["explore_input_search"], self.user, shared)
        else:
            if user_folder["files"]:
                models = user_folder["files"]

        if models:
            for model in models:
                if model["model_user_id"] not in user_ids_name_dict:
                    owner_user = Dynamo().get_user(Dynamo().get_user_email_with_id(model["model_user_id"]))
                    user_ids_name_dict[model["model_user_id"]] = owner_user["user_name"]
                model["owners_name"] = user_ids_name_dict[model["model_user_id"]]

            models = ModelController().sort_models(self.user, models, self.post.get("sort_attribute"), self.post.get("sort_reverse"))

            for index, model in enumerate(models):
                if not model_html:
                    if self.post.get("explore_filter"):
                        if self.post["explore_filter"] == "not_federated":
                            if model["model_is_federated"]:
                                continue
                        elif self.post["explore_filter"] == "favorite":
                            if not model["model_id"] in self.user.user_favorited_models:
                                continue
                        elif self.post["explore_filter"] != model["model_category"]:
                            continue
                    if shared:
                        if not model["model_is_accessible"] and not self.post.get("folder_id") and not self.post.get("explore_input_search"):
                            continue
                        html = ReadWrite().read_html("panel_shared_project/_codes/html_user_folder_rows")
                    else:
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_user_folder_rows")
                elif model_html == "update":
                    if model["model_is_federated"] or (model_to_be_updated["model_format"] == "ifc" and model["model_format"] != "ifc") or (model_to_be_updated["model_format"] in ["fbx", "glb"] and model["model_format"] == "ifc") or (model_to_be_updated["model_id"] == model["model_id"]):
                        continue
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_update_model_user_folder_rows")
                elif model_html == "move":
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_move_model_user_folder_rows")
                elif model_html == "move_folder":
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_move_folder_model_user_folder_rows")
                elif model_html == "create_federated":
                    if model["model_is_federated"] or model["model_format"] != "ifc":
                        continue
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_create_federated_model_user_folder_rows")

                if shared and self.post.get("folder_id"):
                    html.esc("remove_model_visibility_val", "display:none;")

                html.esc("index_val", str(index))
                html.esc("model_id_val", model["model_id"])
                html.esc("owners_name_val", model["owners_name"])

                if model["model_is_federated"]:
                    html.esc("model_icon_val", "note_stack")
                    html.esc("model_update_visibility_val", "display:none;")
                    html.esc("model_category_visibility_val", "display:none;")

                else:
                    if model["model_category"]:
                        html.esc("model_icon_val", model["model_category"] + "_category")
                    else:
                        html.esc("model_icon_val", "note")

                html.esc("model_filename_val", model["model_filename"])
                html.esc("model_name_val", model["model_name"])
                html.esc("model_created_at_val", ModelController().convert_model_created_at_to_date(model["created_at"]))
                html.esc("model_filesize_val", ModelController().convert_model_filesize_to_mb(model["model_filesize"]))

                if ModelController().check_if_model_is_too_big(model["model_filesize"]):
                    html.esc("html_need_to_upgrade_your_plan", self.show_html_need_to_upgrade_your_plan(index))

                html.esc("model_share_link_val", model["model_share_link"])
                html.esc("model_share_link_qrcode_val", model["model_share_link_qrcode"])
                html.esc("model_is_password_protected_val", model["model_is_password_protected"])
                html.esc("model_password_val", model["model_password"])
                html.esc("model_category_val", model["model_category"])
                # html.esc("model_upload_path_zip_val", S3().generate_presigned_url(lambda_constants["processed_bucket"], model["model_upload_path_zip"]))
                html.esc("model_upload_path_zip_val", ModelController().generate_model_download_link(model))

                html.esc("model_is_accessible_val", model["model_is_accessible"])

                if model["model_id"] in self.user.user_favorited_models:
                    html.esc("html_model_is_favorite", self.show_html_model_is_favorite())
                    html.esc("opposite_model_is_favorite_val", False)
                    html.esc("favorite_or_unfavorite_val", self.translate("Desfavoritar"))
                    html.esc("favorite_icon_val", "star")
                else:
                    html.esc("opposite_model_is_favorite_val", True)
                    html.esc("favorite_or_unfavorite_val", self.translate("Favoritar"))
                    html.esc("favorite_icon_val", "star_black")

                if model["model_used_in_federated_ids"]:
                    html.esc("model_used_in_federated_ids_val", True)
                else:
                    html.esc("model_used_in_federated_ids_val", False)

                full_html.append(str(html))
        return "".join(full_html)

    def show_html_need_to_upgrade_your_plan(self, index):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_need_to_upgrade_your_plan")
        html.esc("index_val", str(index))
        return str(html)

    def show_html_model_is_favorite(self):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_model_is_favorite")
        return str(html)

    def show_html_update_modal_update_confirm(self, original_model, new_model):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_update_modal_update_confirm")
        html.esc("original_model_name_val", original_model["model_name"])
        html.esc("original_model_filename_val", original_model["model_filename"])
        html.esc("original_created_at_val", ModelController().convert_model_created_at_to_date(original_model["created_at"]))
        html.esc("new_model_name_val", new_model["model_name"])
        html.esc("new_model_filename_val", new_model["model_filename"])
        html.esc("new_created_at_val", ModelController().convert_model_created_at_to_date(new_model["created_at"]))
        return str(html)

    def list_html_uploading_file_formats(self, file_formats):
        full_html = []
        for format, quantity in file_formats.items():
            html = ReadWrite().read_html("panel_create_project/_codes/html_uploading_file_formats")
            html.esc("file_format_val", format.upper())
            html.esc("file_format_quantity_val", quantity)
            full_html.append(str(html))
        return "".join(full_html)
