from python_web_frame.base_page import BasePage
from utils.utils.ReadWrite import ReadWrite
from utils.utils.StrFormat import StrFormat
from utils.utils.Date import Date
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Ses import Ses
from utils.Config import lambda_constants
from objects.Order import generate_order_short_id, translate_order_type, translate_order_status, check_if_order_is_in_refund_time, translate_order_nfse_status


class BackofficePage(BasePage):
    def __init__(self) -> None:
        super().__init__()
        self.admin = True

    def list_html_backoffice_models_table_rows(self, all_models):
        full_html = []
        if all_models:
            for model in all_models:
                if self.post.get("model_state"):
                    if (self.post["model_state"] != model["model_state"]) and (self.post["model_state"] != "all"):
                        continue
                html = ReadWrite().read_html("backoffice_models/_codes/html_backoffice_models_table_rows")
                html.esc("model_id_val", model["model_id"])
                html.esc("model_user_id_val", model["model_user_id"])
                html.esc("model_project_id_val", model["model_project_id"])
                html.esc("model_user_id_state_val", model["model_user_id_state"])
                html.esc("model_folder_id_val", model["model_folder_id"])
                html.esc("model_branch_id_val", model["model_branch_id"])
                html.esc("model_branch_url_val", model["model_branch_url"])
                html.esc("model_branch_url_qrcode_val", model["model_branch_url_qrcode"])
                html.esc("model_name_val", model["model_name"])
                html.esc("model_code_val", model["model_code"])
                html.esc("model_filehash_val", model["model_filehash"])
                html.esc("model_filename_val", model["model_filename"])
                html.esc("model_filename_zip_val", model["model_filename_zip"])
                html.esc("model_format_val", model["model_format"])
                html.esc("model_is_federated_val", model["model_is_federated"])
                html.esc("model_used_in_federated_ids_val", model["model_used_in_federated_ids"])
                html.esc("model_federated_required_ids_val", model["model_federated_required_ids"])
                html.esc("model_upload_path_zip_val", model["model_upload_path_zip"])
                html.esc("model_upload_path_xml_val", model["model_upload_path_xml"])
                html.esc("model_upload_path_aug_val", model["model_upload_path_aug"])
                html.esc("model_upload_path_sd_aug_val", model["model_upload_path_sd_aug"])
                html.esc("model_upload_path_bin_val", model["model_upload_path_bin"])
                html.esc("model_upload_path_mini_bin_val", model["model_upload_path_mini_bin"])
                html.esc("model_upload_path_glb_val", model["model_upload_path_glb"])
                html.esc("model_filesize_val", model["model_filesize"])
                html.esc("model_filesize_bracket_val", model["model_filesize_bracket"])
                html.esc("model_filesize_zip_val", model["model_filesize_zip"])
                html.esc("model_filesize_xml_val", model["model_filesize_xml"])
                html.esc("model_filesize_aug_val", model["model_filesize_aug"])
                html.esc("model_filesize_sd_aug_val", model["model_filesize_sd_aug"])
                html.esc("model_filesize_bin_val", model["model_filesize_bin"])
                html.esc("model_filesize_mini_bin_val", model["model_filesize_mini_bin"])
                html.esc("model_filesize_glb_val", model["model_filesize_glb"])
                html.esc("model_upload_path_val", model["model_upload_path"])
                html.esc("model_category_val", model["model_category"])
                html.esc("model_password_val", model["model_password"])
                html.esc("model_is_accessible_val", model["model_is_accessible"])
                html.esc("model_is_password_protected_val", model["model_is_password_protected"])
                html.esc("model_sw_version_val", model["model_sw_version"])
                html.esc("model_plugin_version_val", model["model_plugin_version"])
                html.esc("model_thumb_filename_val", model["model_thumb_filename"])
                html.esc("model_zip_key_val", model["model_zip_key"])
                html.esc("model_share_link_val", model["model_share_link"])
                html.esc("model_share_link_qrcode_val", model["model_share_link_qrcode"])
                html.esc("model_category_val", model["model_category"])
                html.esc("model_xml_ec2_machine_val", model["model_xml_ec2_machine"])
                html.esc("model_aug_ec2_machine_val", model["model_aug_ec2_machine"])
                html.esc("model_aug_sd_ec2_machine_val", model["model_aug_sd_ec2_machine"])
                html.esc("model_memory_usage_in_gbs_val", model["model_memory_usage_in_gbs"])
                html.esc("model_was_processed_where_val", model["model_was_processed_where"])
                html.esc("model_xml_started_val", model["model_xml_started"])
                html.esc("model_xml_memory_usage_val", model["model_xml_memory_usage"])
                html.esc("model_xml_completed_val", model["model_xml_completed"])
                html.esc("model_xml_total_time_val", model["model_xml_total_time"])
                html.esc("model_xml_to_dynamo_start_val", model["model_xml_to_dynamo_start"])
                html.esc("model_xml_to_dynamo_completed_val", model["model_xml_to_dynamo_completed"])
                html.esc("model_xml_to_dynamo_total_time_val", model["model_xml_to_dynamo_total_time"])
                html.esc("model_aug_started_val", model["model_aug_started"])
                html.esc("model_aug_percent_val", model["model_aug_percent"])
                html.esc("model_aug_memory_usage_val", model["model_aug_memory_usage"])
                html.esc("model_aug_completed_val", model["model_aug_completed"])
                html.esc("model_aug_total_time_val", model["model_aug_total_time"])
                html.esc("model_aug_sd_started_val", model["model_aug_sd_started"])
                html.esc("model_aug_sd_percent_val", model["model_aug_sd_percent"])
                html.esc("model_aug_sd_memory_usage_val", model["model_aug_sd_memory_usage"])
                html.esc("model_aug_sd_completed_val", model["model_aug_sd_completed"])
                html.esc("model_aug_sd_total_time_val", model["model_aug_sd_total_time"])
                html.esc("model_processing_total_time_val", model["model_processing_total_time"])
                html.esc("model_processing_percentage_val", model["model_processing_percentage"])
                html.esc("model_state_val", model["model_state"])
                html.esc("model_valid_until_val", Date().format_unixtime_to_br_date(model["model_valid_until"]))
                html.esc("created_at_val", Date().format_unixtime_to_br_date(model["created_at"]))
                if model["model_state"] != "completed" or model["model_category"] == "federated":
                    html.esc("reprocess_button_visitility_val", "display:none;")
                full_html.append(str(html))
        return "".join(full_html)

    def list_html_backoffice_users_table_rows(self, users):
        full_html = []
        if users:
            for user in users:
                html = ReadWrite().read_html("backoffice_users/_codes/html_backoffice_users_table_rows")
                html.esc("user_id_val", user["user_id"])
                html.esc("user_email_val", user["user_email"])
                html.esc("user_name_val", user["user_name"])
                html.esc("user_phone_val", user["user_phone"])
                if user["user_client_type"] == "physical":
                    html.esc("user_cpf_or_cnpj_val", user["user_cpf"])
                if user["user_client_type"] == "company":
                    html.esc("user_cpf_or_cnpj_val", user["user_cnpj"])
                html.esc("user_client_type_val", user["user_client_type"])
                html.esc("user_subscription_status_val", user["user_subscription_status"])
                html.esc("user_plan_id_val", user["user_plan_id"])
                html.esc("user_last_login_at_val", Date().format_unixtime_to_br_date(user["user_last_login_at"]))
                html.esc("user_cart_currency_val", user["user_cart_currency"])
                html.esc("user_country_val", user["user_address_data"]["user_country"])
                html.esc("user_auth_token_val", user["user_auth_token"])
                full_html.append(str(html))
        return "".join(full_html)

    def list_html_backoffice_coupons_table_rows(self, coupons):
        full_html = []
        if coupons:
            for coupon in coupons:
                html = ReadWrite().read_html("backoffice_coupons/_codes/html_backoffice_coupons_table_rows")
                html.esc("coupon_name_val", coupon["coupon_name"])
                html.esc("coupon_code_val", coupon["coupon_code"])
                html.esc("coupon_description_val", coupon["coupon_description"])
                html.esc("coupon_available_for_limited_time_val", coupon["coupon_available_for_limited_time"])
                if coupon["coupon_available_for_limited_time"]:
                    html.esc("coupon_start_date_val", Date().format_unixtime_to_br_datetime(coupon["coupon_start_date"]))
                    html.esc("coupon_end_date_val", Date().format_unixtime_to_br_datetime(coupon["coupon_end_date"]))
                else:
                    html.esc("coupon_start_date_val", "-")
                    html.esc("coupon_end_date_val", "-")
                html.esc("coupon_has_limited_uses_count_val", coupon["coupon_has_limited_uses_count"])
                html.esc("coupon_actual_uses_count_val", coupon["coupon_actual_uses_count"])
                html.esc("coupon_maxium_uses_count_val", coupon["coupon_maxium_uses_count"])
                html.esc("coupon_discount_type_val", coupon["coupon_discount_type"])
                html.esc("coupon_brl_discount_val", coupon["coupon_brl_discount"])
                html.esc("coupon_usd_discount_val", coupon["coupon_usd_discount"])
                html.esc("coupon_percentage_discount_val", coupon["coupon_percentage_discount"])
                html.esc("coupon_recurrence_months_val", coupon["coupon_recurrence_months"])
                html.esc("coupon_available_monthly_val", coupon["coupon_available_monthly"])
                html.esc("coupon_available_annually_val", coupon["coupon_available_annually"])
                html.esc("coupon_available_in_brl_val", coupon["coupon_available_in_brl"])
                html.esc("coupon_available_in_usd_val", coupon["coupon_available_in_usd"])
                html.esc("coupons_plans_ids_val", coupon["coupons_plans_ids"])
                html.esc("created_at_val", Date().format_unixtime_to_br_datetime(coupon["created_at"]))
                full_html.append(str(html))
        return "".join(full_html)

    def list_html_coupon_available_plans(self, plans):
        full_html = []
        if plans:
            for index, plan in enumerate(plans):
                if (plan["plan_id"] == lambda_constants["free_plan_id"]) or (plan["plan_is_trial"]):
                    continue
                html = ReadWrite().read_html("backoffice_create_coupon/_codes/html_cupon_available_plans")
                if self.post and self.post.get("coupons_plans_ids") and (plan["plan_id"] in self.post["coupons_plans_ids"]):
                    html.esc("coupon_plan_checked_val", "checked='checked'")
                html.esc("index_val", index)
                html.esc("plan_id_val", plan["plan_id"])
                html.esc("plan_name_val", plan["plan_name_pt"])
                full_html.append(str(html))
        return "".join(full_html)

    def send_refund_order_email(self, user_email, order_id):
        html = ReadWrite().read_html("backoffice_orders/_codes/html_email_order_refund")
        html.esc("order_id_val", order_id)
        Ses().send_email(user_email, body_html=str(html), body_text=str(html), subject_data="Augin - " + self.translate("Sua compra está sendo reembolsada"))

    def list_html_backoffice_orders_table_rows(self, all_orders):
        plan_id_plan = {}
        full_html = []
        if all_orders:
            for order in all_orders:
                if self.post.get("search_order_status"):
                    if (self.post["search_order_status"] != order["order_status"]) and (self.post["search_order_status"] != "all"):
                        continue
                html = ReadWrite().read_html("backoffice_orders/_codes/html_backoffice_orders_table_rows")
                html.esc("order_user_id_val", order["order_user_id"])
                html.esc("order_short_id_val", generate_order_short_id(order["order_id"]))
                html.esc("order_last_error_message_val", order.get("order_last_error_message"))
                html.esc("order_payment_method", StrFormat().format_to_payment_method(order["order_payment_method"]))
                html.esc("order_datetime_val", Date().format_unixtime_to_br_datetime(order["created_at"]))
                html.esc("order_type_val", translate_order_type(order["order_type"]))
                if order.get("order_user_cart_coupon_code"):
                    html.esc("order_user_cart_coupon_code_val", order["order_user_cart_coupon_code"])
                else:
                    html.esc("order_user_cart_coupon_code_val", "-")

                if order["order_plan_id"] not in plan_id_plan:
                    plan_id_plan[order["order_plan_id"]] = Dynamo().get_plan(order["order_plan_id"])
                html.esc("order_plan_name_val", plan_id_plan[order["order_plan_id"]]["plan_name_" + self.lang])
                html.esc("order_currency_val", StrFormat().format_currency_to_symbol(order["order_currency"]))
                html.esc("order_total_price_val", StrFormat().format_to_money(order["order_total_price"], order["order_currency"]))
                html.esc("order_status_val", translate_order_status(order["order_status"]))
                if order["order_status"] == "paid" and order["order_payment_method"] == "card" and check_if_order_is_in_refund_time(order["created_at"]):
                    html.esc("html_refund_order", self.show_html_refund_order(order["order_id"]))
                html.esc("order_nfse_xml_link_val", order["order_nfse_xml_link"])
                html.esc("order_nfse_pdf_link_val", order["order_nfse_pdf_link"])
                html.esc("order_nfse_status_val", translate_order_nfse_status(order.get("order_nfse_status", "")))
                if order["order_status"] == "paid" and order["order_nfse_status"] == "not_issued":
                    html.esc("html_re_issue_order_nfse", self.show_html_re_issue_order_nfse(order["order_id"]))
                if order["order_status"] == "paid" and order["order_nfse_pdf_link"] == "":
                    html.esc("html_re_issue_order_nfse_pdf", self.show_html_re_issue_order_nfse_pdf(order["order_id"]))
                if order["order_status"] not in ["paid", "refunded"]:
                    html.esc("order_link_visibility_val", 'style="display:none;"')
                full_html.append(str(html))
        return "".join(full_html)

    def show_html_refund_order(self, order_id):
        html = ReadWrite().read_html("backoffice_orders/_codes/html_refund_order")
        html.esc("order_id_val", order_id)
        return str(html)

    def show_html_re_issue_order_nfse_pdf(self, order_id):
        html = ReadWrite().read_html("backoffice_orders/_codes/html_re_issue_order_nfse_pdf")
        html.esc("order_id_val", order_id)
        return str(html)

    def show_html_re_issue_order_nfse(self, order_id):
        html = ReadWrite().read_html("backoffice_orders/_codes/html_re_issue_order_nfse")
        html.esc("order_id_val", order_id)
        return str(html)

    def list_html_plan_reference_tracker_options(self):
        full_html = []
        for plan_reference_tracker in lambda_constants["plan_reference_trackers"]:
            html = ReadWrite().read_html("backoffice_create_plan/_codes/html_plan_reference_tracker_options")
            html.esc("plan_reference_tracker_val", lambda_constants["plan_reference_trackers"][plan_reference_tracker])
            html.esc("plan_reference_tracker_name_val", self.translate(plan_reference_tracker))
            if self.post.get("plan_reference_tracker") == lambda_constants["plan_reference_trackers"][plan_reference_tracker] or (self.path.get("plan") and self.path["plan"].get("plan_reference_tracker") == lambda_constants["plan_reference_trackers"][plan_reference_tracker]):
                html.esc("pre_sel_val", "selected='selected'")
            full_html.append(str(html))
        return "".join(full_html)

    def list_html_backoffice_plans_table_rows(self, plans):
        full_html = []
        if plans:
            for plan in plans:
                html = ReadWrite().read_html("backoffice_plans/_codes/html_backoffice_plans_table_rows")
                if plan["plan_is_trial"]:
                    html.esc("edit_plan_visibility_val", "display:none;")
                html.esc("plan_id_val", plan["plan_id"])
                html.esc("plan_name_pt_val", plan["plan_name_pt"])
                html.esc("plan_name_en_val", plan["plan_name_en"])
                html.esc("plan_name_es_val", plan["plan_name_es"])
                html.esc("plan_description_pt_val", plan["plan_description_pt"])
                html.esc("plan_description_en_val", plan["plan_description_en"])
                html.esc("plan_description_es_val", plan["plan_description_es"])
                html.esc("plan_available_for_purchase_val", plan["plan_available_for_purchase"])
                html.esc("plan_available_annually_val", plan["plan_available_annually"])
                html.esc("plan_price_annually_brl_val", plan["plan_price_annually_brl"])
                html.esc("plan_price_annually_usd_val", plan["plan_price_annually_usd"])
                html.esc("plan_annually_card_payment_method_val", plan["plan_annually_card_payment_method"])
                html.esc("plan_annually_boleto_payment_method_val", plan["plan_annually_boleto_payment_method"])
                html.esc("plan_annually_pix_payment_method_val", plan["plan_annually_pix_payment_method"])
                html.esc("plan_available_monthly_val", plan["plan_available_monthly"])
                html.esc("plan_price_monthly_brl_val", plan["plan_price_monthly_brl"])
                html.esc("plan_price_monthly_usd_val", plan["plan_price_monthly_usd"])
                html.esc("plan_monthly_card_payment_method_val", plan["plan_monthly_card_payment_method"])
                html.esc("plan_cloud_space_in_mbs_val", plan["plan_cloud_space_in_mbs"])
                html.esc("plan_maxium_model_size_in_mbs_val", plan["plan_maxium_model_size_in_mbs"])
                html.esc("plan_maxium_federated_size_in_mbs_val", plan["plan_maxium_federated_size_in_mbs"])
                html.esc("plan_reference_tracker_val", plan["plan_reference_tracker"])
                html.esc("plan_maxium_devices_available_val", plan["plan_maxium_devices_available"])
                html.esc("plan_maxium_devices_changes_in_30d_val", plan["plan_maxium_devices_changes_in_30d"])
                html.esc("plan_has_trial_val", plan["plan_has_trial"])
                html.esc("plan_is_trial_val", plan["plan_is_trial"])
                html.esc("plan_trial_duration_in_days_val", plan["plan_trial_duration_in_days"])
                html.esc("plan_app_can_be_offline_in_days_val", plan["plan_app_can_be_offline_in_days"])
                full_html.append(str(html))
        return "".join(full_html)

    def show_html_pagination(self, itens_actual_count, itens_total_count, query, last_evaluated_key, query_filter=""):
        html = ReadWrite().read_html("main/_codes/html_pagination")
        html.esc("itens_actual_count_val", itens_actual_count)
        html.esc("itens_total_count_val", itens_total_count)
        html.esc("query_val", query)
        if query_filter:
            html.esc("query_filter_val", query_filter)
        if self.post.get("showing_total_count"):
            html.esc("last_scroll_position_val", self.post.get("last_scroll_position", "0"))
        if not itens_total_count:
            html.esc("pagination_visibility_val", "display: none;")
        elif not last_evaluated_key:
            html.esc("pagination_visibility_val", "display: none;")
        else:
            if str(itens_actual_count) == "0" or str(itens_total_count) == "0":
                html.esc("pagination_visibility_val", "display: none;")
            if int(itens_actual_count) == int(itens_total_count):
                html.esc("pagination_visibility_val", "display: none;")
        return str(html)
