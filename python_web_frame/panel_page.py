from python_web_frame.base_page import BasePage
from utils.utils.Sort import Sort
from utils.utils.ReadWrite import ReadWrite
from utils.AWS.Dynamo import Dynamo
from python_web_frame.controllers.model_controller import ModelController


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

    def list_html_user_folder_rows(self):
        full_html = []
        if self.user.user_dicts:
            if self.user.user_dicts["folders"]:
                for folder in self.user.user_dicts["folders"]:
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_user_folder_rows")
                    full_html.append(str(html))
            if self.user.user_dicts["files"]:
                folder_models = []
                for model_id in self.user.user_dicts["files"]:
                    folder_models.append(Dynamo().get_model_by_id(model_id))

                folder_models = ModelController().sort_models(folder_models)
                for index, model in enumerate(folder_models):
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_user_folder_rows")

                    html.esc("index_val", str(index))
                    html.esc("model_id_val", model["model_id"])

                    if model.get("model_is_federated"):
                        html.esc("model_icon_val", "note_stack")
                    else:
                        html.esc("model_icon_val", "note")

                    html.esc("model_filename_val", model["model_filename"])
                    html.esc("model_created_at_val", ModelController().convert_model_created_at_to_date(model["created_at"]))
                    html.esc("model_filesize_ifc_val", ModelController().convert_model_filesize_ifc_to_mb(model["model_filesize_ifc"]))

                    if ModelController().check_if_model_is_too_big(model["model_filesize_ifc"]):
                        html.esc("html_need_to_upgrade_your_plan", self.show_html_need_to_upgrade_your_plan(index))

                    html.esc("model_share_link_val", model["model_share_link"])
                    html.esc("model_share_link_qrcode_val", model["model_share_link_qrcode"])
                    html.esc("model_is_password_protected_val", model["model_is_password_protected"])
                    html.esc("model_password_val", model["model_password"])

                    if model.get("model_is_favorite"):
                        html.esc("html_model_is_favorite", self.show_html_model_is_favorite())
                        html.esc("opposite_model_is_favorite_val", False)
                    else:
                        html.esc("opposite_model_is_favorite_val", True)

                    full_html.append(str(html))
        return "".join(full_html)

    def show_html_need_to_upgrade_your_plan(self, index):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_need_to_upgrade_your_plan")
        html.esc("index_val", str(index))
        return str(html)

    def show_html_model_is_favorite(self):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_model_is_favorite")
        return str(html)
