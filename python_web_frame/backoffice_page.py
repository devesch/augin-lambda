from python_web_frame.base_page import BasePage
from utils.utils.ReadWrite import ReadWrite
from utils.Config import lambda_constants


class BackofficePage(BasePage):
    def __init__(self) -> None:
        super().__init__()

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
