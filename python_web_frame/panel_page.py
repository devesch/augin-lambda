from python_web_frame.base_page import BasePage
from utils.Config import lambda_constants
from utils.utils.Sort import Sort
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Date import Date
from utils.AWS.Dynamo import Dynamo
from utils.utils.StrFormat import StrFormat
from python_web_frame.controllers.model_controller import ModelController
from objects.Order import translate_order_status
from objects.User import sort_user_folders
from objects.UserFolder import generate_folder_data, increase_folder_visualization_count


class PanelPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

    def show_html_filter_and_search_section(self, show_search=True):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_filter_and_search_section")
        html.esc("html_project_filter_options", self.list_html_project_filter_options())
        if not show_search:
            html.esc("search_project_visibility_val", "display:none;")
        return str(html)

    def list_html_project_filter_options(self):
        full_html = []
        for category_id, category in lambda_constants["available_categories"].items():
            html = ReadWrite().read_html("panel_explore_project/_codes/html_project_filter_option")
            html.esc("category_val", category_id)
            html.esc("category_name_val", self.translate(category["category_name"]))
            full_html.append(str(html))

        html = ReadWrite().read_html("panel_explore_project/_codes/html_project_filter_option")
        html.esc("category_val", "favorite")
        html.esc("category_name_val", self.translate("Favoritos"))
        full_html.append(str(html))
        html = ReadWrite().read_html("panel_explore_project/_codes/html_project_filter_option")
        html.esc("category_val", "not_federated")
        html.esc("category_name_val", self.translate("Não Federados"))
        full_html.append(str(html))
        return "".join(full_html)

    def show_html_create_federated_button(self):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_create_federated_button")
        return str(html)

    def list_html_edit_federated_model_rows(self, federated_required_models):
        full_html = []
        if federated_required_models:
            for federated_required_models in federated_required_models:
                html = ReadWrite().read_html("panel_explore_project/_codes/html_edit_federated_model_rows")
                html.esc("model_name_val", federated_required_models["model_name"])
                html.esc("model_id_val", federated_required_models["model_id"])
                full_html.append(str(html))
        return "".join(full_html)

    def show_html_make_an_upgrade_link(self):
        html = ReadWrite().read_html("panel_create_project/_codes/html_make_an_upgrade_link")
        return str(html)

    def list_html_uploading_models(self, models_not_created):
        full_html = []
        if models_not_created:
            for index, model in enumerate(models_not_created):
                full_html.append(str(self.show_html_uploading_models(model["model_filename"], index, full_model=model)))
        return "".join(full_html)

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

    def show_html_uploading_models(self, model_filename, index, full_model=False):
        html = ReadWrite().read_html("panel_create_project/_codes/html_uploading_models")
        html.esc("model_filename_val", model_filename)
        html.esc("index_val", index)
        if full_model:
            html.esc("model_id_val", full_model["model_id"])
            if full_model["model_format"] != "ifc":
                html.esc("has_fbx_val", "True")
            html.esc("actual_progress_val", "100")
            html.esc("uploading_element_message_val", self.translate("Upload realizado com sucesso."))
            html.esc("success_class_val", "success")
            html.esc("html_uploading_file_formats", self.list_html_uploading_file_formats({full_model["model_format"]: "1"}))
        else:
            html.esc("actual_progress_val", "0")
            html.esc("uploading_element_message_val", self.translate("Enviando arquivo, aguarde"))

        return str(html)

    def list_html_user_folder_rows(self, user_plan=None, folder_id=None, model_html=""):
        full_html = []
        shared = False
        federated_model = None

        if self.user:
            user_ids_name_dict = {self.user.user_id: self.user.user_name}
        else:
            user_ids_name_dict = {}

        if self.route == "panel_shared_project" or self.post.get("page") == "panel_shared_project" or self.route == "view_folder" or self.post.get("page") == "view_folder":
            shared = True

        if self.post.get("federated_model_id"):
            federated_model = Dynamo().get_model(self.post["federated_model_id"])

        if self.post.get("model_id_to_be_updated"):
            model_to_be_updated = Dynamo().get_model(self.post.get("model_id_to_be_updated"))

        if not self.post.get("explore_input_search"):
            if folder_id:
                user_folder = Dynamo().get_folder(folder_id)
            else:
                if shared:
                    user_folder = Dynamo().get_folder(self.user.user_shared_dicts_folder_id)
                else:
                    user_folder = Dynamo().get_folder(self.user.user_dicts_folder_id)

            if (shared and not self.user) or (shared and user_folder["folder_user_id"] != self.user.user_id):
                user_folder = increase_folder_visualization_count(user_folder)
            user_folder = generate_folder_data(user_folder)
            if user_folder["folders"]:

                for folder in user_folder["folders"]:
                    if folder["folder_user_id"] not in user_ids_name_dict:
                        owner_user = self.load_user(folder["folder_user_id"])
                        user_ids_name_dict[folder["folder_user_id"]] = owner_user.user_name
                    folder["owners_name"] = user_ids_name_dict[folder["folder_user_id"]]

                user_folder["folders"] = sort_user_folders(self.user, user_folder["folders"], self.post.get("sort_attribute"), self.post.get("sort_reverse"))
                for folder in user_folder["folders"]:
                    if not model_html:
                        if shared:
                            if not folder["folder_is_accessible"] and not folder_id:
                                continue
                            html = ReadWrite().read_html("panel_shared_project/_codes/html_user_folder_rows_folders")
                            if not self.user:
                                html.esc("actions_visibility_val", "display:none;")
                        else:
                            html = ReadWrite().read_html("panel_explore_project/_codes/html_user_folder_rows_folders")
                            if user_plan and user_plan.get("plan_share_files"):
                                html.esc("html_share_folder_button", self.show_html_share_folder_button(folder))
                            if user_plan and user_plan.get("plan_download_files") and (folder["folders"] or folder["files"]):
                                html.esc("html_download_folder_button", self.show_html_download_folder_button(folder))

                    elif model_html == "update":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_update_model_user_folder_rows_folders")
                    elif model_html == "move":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_move_model_user_folder_rows_folders")
                    elif model_html == "move_folder":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_move_folder_model_user_folder_rows_folders")
                    elif model_html == "create_federated":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_create_federated_model_user_folder_rows_folders")
                    elif model_html == "add_project_to_federated":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_add_project_to_federated_model_user_folder_rows_folders")
                    if shared and folder_id:
                        html.esc("remove_folder_visibility_val", "display:none;")

                    html.esc("folder_path_val", folder["folder_path"])
                    html.esc("folder_name_val", folder["folder_name"])
                    html.esc("folder_id_val", folder["folder_id"])
                    html.esc("folder_created_at_val", Date().format_to_str_time(folder["created_at"]))
                    html.esc("folder_size_in_mbs_val", f'{round(float(folder["folder_size_in_mbs"]), 2):.1f}' + " Mb")
                    html.esc("owners_name_val", folder["owners_name"])

                    if self.user and folder["folder_id"] in self.user.user_favorited_folders:
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
                    owner_user = self.load_user(model["model_user_id"])
                    user_ids_name_dict[model["model_user_id"]] = owner_user.user_name
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
                        if not model["model_is_accessible"] and not folder_id and not self.post.get("explore_input_search"):
                            continue
                        html = ReadWrite().read_html("panel_shared_project/_codes/html_user_folder_rows")
                        if not self.user:
                            html.esc("actions_visibility_val", "display:none;")
                    else:
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_user_folder_rows")
                        if user_plan and user_plan.get("plan_share_files"):
                            html.esc("html_share_project_button", self.show_html_share_project_button(model))
                        if user_plan and user_plan.get("plan_download_files"):
                            html.esc("html_download_project_button", self.show_html_download_project_button(model))

                elif model_html == "update":
                    if model["model_is_federated"] or (model_to_be_updated["model_format"] == "ifc" and model["model_format"] != "ifc") or (model_to_be_updated["model_format"] in ["fbx", "glb"] and model["model_format"] == "ifc") or (model_to_be_updated["model_id"] == model["model_id"]):
                        continue
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_update_model_user_folder_rows")
                elif model_html == "move":
                    if index == 5:
                        break
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_move_model_user_folder_rows")
                elif model_html == "move_folder":
                    if index == 5:
                        break
                    html = ReadWrite().read_html("panel_explore_project/_codes/html_move_folder_model_user_folder_rows")
                elif model_html == "create_federated" or "add_project_to_federated":
                    if model["model_is_federated"] or model["model_format"] != "ifc":
                        continue
                    if model_html == "create_federated":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_create_federated_model_user_folder_rows")
                    if model_html == "add_project_to_federated":
                        html = ReadWrite().read_html("panel_explore_project/_codes/html_add_project_to_federated_model_user_folder_rows")
                        # if federated_model and model["model_id"] in federated_model["model_federated_required_ids"]:
                        #     html.esc("checked_val", "checked='checked'")

                if shared and folder_id:
                    html.esc("remove_model_visibility_val", "display:none;")

                html.esc("index_val", str(index))
                html.esc("model_id_val", model["model_id"])
                html.esc("model_name_val", model["model_name"])
                html.esc("owners_name_val", model["owners_name"])

                if model["model_is_federated"]:
                    html.esc("model_icon_val", "note_stack")
                    html.esc("model_update_visibility_val", "display:none;")
                    html.esc("model_category_visibility_val", "display:none;")
                    html.esc("model_federated_required_ids_val", ",".join(model["model_federated_required_ids"]))

                else:
                    html.esc("model_edit_federated_visibility_val", "display:none;")
                    if model["model_category"]:
                        html.esc("model_icon_val", model["model_category"] + "_category")
                    else:
                        html.esc("model_icon_val", "note")

                html.esc("model_filename_val", model["model_filename"])
                html.esc("model_name_val", model["model_name"])
                html.esc("model_created_at_val", Date().format_to_str_time(model["created_at"]))
                html.esc("model_filesize_val", ModelController().convert_model_filesize_to_mb(model["model_filesize"]))

                if ModelController().check_if_model_is_too_big(model["model_filesize"]):
                    html.esc("html_need_to_upgrade_your_plan", self.show_html_need_to_upgrade_your_plan(index))

                html.esc("model_category_val", model["model_category"])
                # html.esc("model_upload_path_zip_val", S3().generate_presigned_url(lambda_constants["processed_bucket"], model["model_upload_path_zip"]))
                html.esc("model_upload_path_zip_val", ModelController().generate_model_download_link(model))

                if self.user and model["model_id"] in self.user.user_favorited_models:
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

    def show_html_download_folder_button(self, folder):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_download_folder_button")
        html.esc("folder_id_val", folder["folder_id"])
        return str(html)

    def show_html_share_folder_button(self, folder):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_share_folder_button")
        html.esc("folder_name_val", folder["folder_name"])
        html.esc("folder_id_val", folder["folder_id"])
        html.esc("folder_password_val", folder["folder_password"])
        html.esc("folder_is_accessible_val", folder["folder_is_accessible"])
        html.esc("folder_visualization_count_val", folder["folder_visualization_count"])
        html.esc("folder_share_link_val", folder["folder_share_link"])
        html.esc("folder_share_link_qrcode_val", folder["folder_share_link_qrcode"])
        html.esc("folder_is_password_protected_val", folder["folder_is_password_protected"])
        return str(html)

    def show_html_download_project_button(self, model):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_download_project_button")
        html.esc("model_id_val", model["model_id"])
        return str(html)

    def show_html_share_project_button(self, model):
        html = ReadWrite().read_html("panel_explore_project/_codes/html_share_project_button")
        html.esc("model_id_val", model["model_id"])
        html.esc("model_name_val", model["model_name"])
        html.esc("model_share_link_val", model["model_share_link"])
        html.esc("model_share_link_qrcode_val", model["model_share_link_qrcode"])
        html.esc("model_is_password_protected_val", model["model_is_password_protected"])
        html.esc("model_password_val", model["model_password"])
        html.esc("model_is_accessible_val", model["model_is_accessible"])
        return str(html)

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
        html.esc("original_created_at_val", Date().format_to_str_time(original_model["created_at"]))
        html.esc("new_model_name_val", new_model["model_name"])
        html.esc("new_model_filename_val", new_model["model_filename"])
        html.esc("new_created_at_val", Date().format_to_str_time(new_model["created_at"]))
        return str(html)

    def list_html_uploading_file_formats(self, file_formats):
        full_html = []
        for format, quantity in file_formats.items():
            html = ReadWrite().read_html("panel_create_project/_codes/html_uploading_file_formats")
            html.esc("file_format_val", format.upper())
            html.esc("file_format_quantity_val", quantity)
            full_html.append(str(html))
        return "".join(full_html)

    def show_html_payment_history_div(self, user_orders):
        import math

        pages_amount = math.ceil(int(self.user.user_total_orders_count) / int(lambda_constants["user_orders_page_size"]))
        html = ReadWrite().read_html("panel_your_plan/_codes/html_payment_history_div")
        html.esc("html_payment_history_rows", self.list_html_payment_history_rows(user_orders))
        html.esc("payment_history_pages_count_val", pages_amount)
        html.esc("html_payment_history_pages_buttons", self.list_html_payment_history_pages_buttons(pages_amount))
        return str(html)

    def list_html_payment_history_pages_buttons(self, pages_amount):
        full_html = []
        for index in range(pages_amount):
            html = ReadWrite().read_html("panel_your_plan/_codes/html_payment_history_pages_buttons")
            if index == 0:
                html.esc("selected_page_val", "selected-page")
            html.esc("page_index_val", (index + 1))
            full_html.append(str(html))
        return "".join(full_html)

    def list_html_payment_history_rows(self, user_orders):
        plan_id_name_conversion = {}
        full_html = []
        for index, order in enumerate(user_orders):
            html = ReadWrite().read_html("panel_your_plan/_codes/html_payment_history_rows")
            html.esc("order_created_at_val", Date().format_to_str_time(order["created_at"]))
            html.esc("order_currency_symbol_val", StrFormat().format_currency_to_symbol(order["order_currency"]))
            html.esc("order_price_val", StrFormat().format_to_money(order["order_total_price"], order["order_currency"]))
            html.esc("order_status_val", translate_order_status(order["order_status"]))

            if order["order_status"] == "paid":
                html.esc("order_status_class_val", "paid")
            else:
                html.esc("order_status_class_val", "failed")

            if order["order_plan_id"] not in plan_id_name_conversion:
                plan_id_name_conversion[order["order_plan_id"]] = Dynamo().get_plan(order["order_plan_id"])
            html.esc("order_plan_name_val", plan_id_name_conversion[order["order_plan_id"]]["plan_name_" + self.lang])
            html.esc("order_id_val", order["order_id"])

            full_html.append(str(html))
        return "".join(full_html)

    def show_html_payment_methods_div(self, user_payment_methods, user_subscription):
        html = ReadWrite().read_html("panel_your_plan/_codes/html_payment_methods_div")
        html.esc("html_payment_methods_rows", self.list_html_payment_methods_rows(user_payment_methods, user_subscription))
        return str(html)

    def list_html_payment_methods_rows(self, user_payment_methods, user_subscription):
        full_html = []
        for index, payment_method in enumerate(user_payment_methods):
            html = ReadWrite().read_html("panel_your_plan/_codes/html_payment_methods_rows")
            html.esc("payment_method_id_val", payment_method["payment_method_id"])
            html.esc("index_val", (index + 1))
            if (user_subscription) and (user_subscription.get("subscription_default_payment_method") == payment_method["payment_method_id"]):
                html.esc("make_default_payement_method_visibility_val", "display:none;")
                html.esc("html_active_method_icon", self.show_html_active_method_icon())
                html.esc("button_disabled_val", "disabled")
            else:
                html.esc("button_onclick_val", "onclick='js.index.toggleExploreMenu(this)'")
            if payment_method["payment_method_type"] == "card":
                html.esc("brand_val", payment_method["payment_method_card"]["brand"])
                html.esc("title_brand_val", payment_method["payment_method_card"]["brand"].title())
                html.esc("last4_val", payment_method["payment_method_card"]["last4"])
                html.esc("exp_month_val", payment_method["payment_method_card"]["exp_month"])
                html.esc("exp_year_val", payment_method["payment_method_card"]["exp_year"])
            if payment_method["payment_method_type"] == "boleto":
                html.esc("brand_val", self.translate("boleto").title())
                html.esc("expires_in_visibility_val", "display:none;")
            full_html.append(str(html))
        return "".join(full_html)

    def show_html_active_method_icon(self):
        html = ReadWrite().read_html("panel_your_plan/_codes/html_active_method_icon")
        return str(html)
