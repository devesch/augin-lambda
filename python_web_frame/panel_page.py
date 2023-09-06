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
        if self.user.user_dicts:
            user_folder = self.user.generate_folder_data(folder_id)
            if user_folder["folders"]:
                user_folder["folders"] = sort_user_folders(user_folder["folders"], self.post.get("sort_attribute"), self.post.get("sort_reverse"))
                for folder in user_folder["folders"]:
                    if not model_html:
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_user_folder_rows_folders")
                    elif model_html == "update":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_update_model_user_folder_rows_folders")
                    elif model_html == "move":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_move_model_user_folder_rows_folders")
                    elif model_html == "move_folder":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_move_folder_model_user_folder_rows_folders")

                    html.esc("folder_path_val", folder["folder_path"])
                    html.esc("folder_name_val", folder["folder_name"])
                    html.esc("folder_id_val", folder["folder_id"])
                    html.esc("folder_created_at_val", ModelController().convert_model_created_at_to_date(folder["created_at"]))
                    html.esc("folder_size_in_mbs_val", folder["folder_size_in_mbs"] + " Mb")

                    if folder["folder_size_in_mbs"] == "0":
                        html.esc("download_folder_visibility_val", "display:none;")

                    if folder.get("folder_is_favorite"):
                        html.esc("html_folder_is_favorite", self.show_html_model_is_favorite())
                        html.esc("opposite_folder_is_favorite_val", False)
                        html.esc("favorite_or_unfavorite_val", self.translate("Desfavoritar"))
                        html.esc("favorite_icon_val", "star")
                    else:
                        html.esc("opposite_folder_is_favorite_val", True)
                        html.esc("favorite_or_unfavorite_val", self.translate("Favoritar"))
                        html.esc("favorite_icon_val", "star_black")

                    full_html.append(str(html))

            if user_folder["files"]:
                user_folder["files"] = ModelController().sort_models(user_folder["files"], self.post.get("sort_attribute"), self.post.get("sort_reverse"))
                for index, model in enumerate(user_folder["files"]):
                    if not model_html:
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_user_folder_rows")
                    elif model_html == "update":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_update_model_user_folder_rows")
                    elif model_html == "move":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_move_model_user_folder_rows")
                    elif model_html == "move_folder":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_move_folder_model_user_folder_rows")

                    html.esc("index_val", str(index))
                    html.esc("model_id_val", model["model_id"])
                    if model.get("model_is_federated"):
                        html.esc("model_icon_val", "note_stack")
                        html.esc("model_update_visibility_val", "display:none;")
                        html.esc("model_category_visibility_val", "display:none;")

                    else:
                        if model.get("model_category"):
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

                    if model.get("model_is_favorite"):
                        html.esc("html_model_is_favorite", self.show_html_model_is_favorite())
                        html.esc("opposite_model_is_favorite_val", False)
                        html.esc("favorite_or_unfavorite_val", self.translate("Desfavoritar"))
                        html.esc("favorite_icon_val", "star")
                    else:
                        html.esc("opposite_model_is_favorite_val", True)
                        html.esc("favorite_or_unfavorite_val", self.translate("Favoritar"))
                        html.esc("favorite_icon_val", "star_black")

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
