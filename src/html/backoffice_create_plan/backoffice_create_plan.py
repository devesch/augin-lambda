from python_web_frame.backoffice_page import BackofficePage
from utils.Config import lambda_constants
from utils.utils.Validation import Validation
from objects.Plan import Plan


class BackofficeCreatePlan(BackofficePage):
    name = "Backoffice - Criar Plano"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()

        if self.post:
            if self.post.get("plan_name_pt"):
                html.esc("plan_name_pt_val", self.post["plan_name_pt"])
            if self.post.get("plan_name_en"):
                html.esc("plan_name_en_val", self.post["plan_name_en"])
            if self.post.get("plan_name_es"):
                html.esc("plan_name_es_val", self.post["plan_name_es"])

            if self.post.get("plan_description_pt"):
                html.esc("plan_description_pt_val", self.post["plan_description_pt"])
            if self.post.get("plan_description_en"):
                html.esc("plan_description_en_val", self.post["plan_description_en"])
            if self.post.get("plan_description_es"):
                html.esc("plan_description_es_val", self.post["plan_description_es"])

            if self.post.get("plan_available_for_purchase"):
                html.esc("plan_available_for_purchase_checked_val", "checked='checked'")

            if self.post.get("plan_available_annually"):
                html.esc("plan_available_annually_checked_val", "checked='checked'")
            else:
                html.esc("annually_div_visibility_val", "display:none;")
            if self.post.get("plan_price_annually_brl"):
                html.esc("plan_price_annually_brl_val", self.post["plan_price_annually_brl"])
            if self.post.get("plan_price_annually_brl_actual"):
                html.esc("plan_price_annually_brl_actual_val", self.post["plan_price_annually_brl_actual"])
            if self.post.get("plan_price_annually_usd"):
                html.esc("plan_price_annually_usd_val", self.post["plan_price_annually_usd"])
            if self.post.get("plan_price_annually_usd_actual"):
                html.esc("plan_price_annually_usd_actual_val", self.post["plan_price_annually_usd_actual"])

            if self.post.get("plan_annually_card_payment_method"):
                html.esc("plan_annually_card_payment_method_checked_val", "checked='checked'")
            if self.post.get("plan_annually_boleto_payment_method"):
                html.esc("plan_annually_boleto_payment_method_checked_val", "checked='checked'")
            if self.post.get("plan_annually_pix_payment_method"):
                html.esc("plan_annually_pix_payment_method_checked_val", "checked='checked'")

            if self.post.get("plan_available_monthly"):
                html.esc("plan_available_monthly_checked_val", "checked='checked'")
            else:
                html.esc("monthly_div_visibility_val", "display:none;")
            if self.post.get("plan_price_monthly_brl"):
                html.esc("plan_price_monthly_brl_val", self.post["plan_price_monthly_brl"])
            if self.post.get("plan_price_monthly_brl_actual"):
                html.esc("plan_price_monthly_brl_actual_val", self.post["plan_price_monthly_brl_actual"])
            if self.post.get("plan_price_monthly_usd"):
                html.esc("plan_price_monthly_usd_val", self.post["plan_price_monthly_usd"])
            if self.post.get("plan_price_monthly_usd_actual"):
                html.esc("plan_price_monthly_usd_actual_val", self.post["plan_price_monthly_usd_actual"])

            if self.post.get("plan_monthly_card_payment_method"):
                html.esc("plan_monthly_card_payment_method_checked_val", "checked='checked'")
            if self.post.get("plan_monthly_boleto_payment_method"):
                html.esc("plan_monthly_boleto_payment_method_checked_val", "checked='checked'")
            if self.post.get("plan_monthly_pix_payment_method"):
                html.esc("plan_monthly_pix_payment_method_checked_val", "checked='checked'")

            if self.post.get("plan_cloud_space_in_mbs"):
                html.esc("plan_cloud_space_in_mbs_val", self.post["plan_cloud_space_in_mbs"])
            if self.post.get("plan_maxium_model_size_in_mbs"):
                html.esc("plan_maxium_model_size_in_mbs_val", self.post["plan_maxium_model_size_in_mbs"])
            if self.post.get("plan_maxium_federated_size_in_mbs"):
                html.esc("plan_maxium_federated_size_in_mbs_val", self.post["plan_maxium_federated_size_in_mbs"])
            if self.post.get("plan_reference_tracker_select"):
                html.esc("plan_reference_tracker_select_val", self.post["plan_reference_tracker_select"])
            if self.post.get("plan_maxium_devices_available"):
                html.esc("plan_maxium_devices_available_val", self.post["plan_maxium_devices_available"])
            if self.post.get("plan_maxium_devices_changes_in_30d"):
                html.esc("plan_maxium_devices_changes_in_30d_val", self.post["plan_maxium_devices_changes_in_30d"])
            if self.post.get("plan_app_can_be_offline_in_days"):
                html.esc("plan_app_can_be_offline_in_days_val", self.post["plan_app_can_be_offline_in_days"])

            if self.post.get("plan_has_trial"):
                html.esc("plan_has_trial_checked_val", "checked='checked'")
            else:
                html.esc("trial_div_visibility_val", "display:none;")
            if self.post.get("plan_trial_duration_in_days"):
                html.esc("plan_trial_duration_in_days_val", self.post["plan_trial_duration_in_days"])
        else:
            html.esc("plan_available_for_purchase_checked_val", "checked='checked'")
            html.esc("plan_available_annually_checked_val", "checked='checked'")
            html.esc("plan_available_monthly_checked_val", "checked='checked'")
            html.esc("plan_has_trial_checked_val", "checked='checked'")

        html.esc("html_plan_reference_tracker_options", self.list_html_plan_reference_tracker_options())

        return str(html)

    def render_post(self):
        if not self.post.get("plan_name_pt"):
            return self.render_get_with_error("É necessárion informar um nome em PT")
        if not self.post.get("plan_name_en"):
            return self.render_get_with_error("É necessárion informar um nome em EN")
        if not self.post.get("plan_name_es"):
            return self.render_get_with_error("É necessárion informar um nome em ES")

        if self.post.get("plan_price_annually_brl"):
            if not Validation().check_if_is_number(self.post["plan_price_annually_brl"]):
                return self.render_get_with_error("O preço do plano anual em BRL deve ser um número")
        if self.post.get("plan_price_annually_brl_actual"):
            if not Validation().check_if_is_number(self.post["plan_price_annually_brl_actual"]):
                return self.render_get_with_error("O preço atual do plano anual em BRL deve ser um número")

        if self.post.get("plan_price_annually_usd"):
            if not Validation().check_if_is_number(self.post["plan_price_annually_usd"]):
                return self.render_get_with_error("O preço do plano anual em USD deve ser um número")
        if self.post.get("plan_price_annually_usd_actual"):
            if not Validation().check_if_is_number(self.post["plan_price_annually_usd_actual"]):
                return self.render_get_with_error("O preço atual do plano anual em USD deve ser um número")

        if self.post.get("plan_price_monthly_brl"):
            if not Validation().check_if_is_number(self.post["plan_price_monthly_brl"]):
                return self.render_get_with_error("O preço do plano mensal em BRL deve ser um número")
        if self.post.get("plan_price_monthly_brl_actual"):
            if not Validation().check_if_is_number(self.post["plan_price_monthly_brl_actual"]):
                return self.render_get_with_error("O preço atual do plano mensal em BRL deve ser um número")

        if self.post.get("plan_price_monthly_usd"):
            if not Validation().check_if_is_number(self.post["plan_price_monthly_usd"]):
                return self.render_get_with_error("O preço do plano mensal em USD deve ser um número")
        if self.post.get("plan_price_monthly_usd_actual"):
            if not Validation().check_if_is_number(self.post["plan_price_monthly_usd_actual"]):
                return self.render_get_with_error("O preço atual do plano mensal em USD deve ser um número")

        if self.post.get("plan_cloud_space_in_mbs"):
            if not Validation().check_if_is_number(self.post["plan_cloud_space_in_mbs"]):
                return self.render_get_with_error("O tamanho máximo em núvem deve ser um número")
        if self.post.get("plan_maxium_model_size_in_mbs"):
            if not Validation().check_if_is_number(self.post["plan_maxium_model_size_in_mbs"]):
                return self.render_get_with_error("O tamanho do modelo máximo deve ser um número")
        if self.post.get("plan_maxium_federated_size_in_mbs"):
            if not Validation().check_if_is_number(self.post["plan_maxium_federated_size_in_mbs"]):
                return self.render_get_with_error("O tamanho de federado máximo deve ser um número")
        if self.post.get("plan_maxium_devices_available"):
            if not Validation().check_if_is_number(self.post["plan_maxium_devices_available"]):
                return self.render_get_with_error("A quantidade máxima de dispositivos deve ser um número")
        if self.post.get("plan_maxium_devices_changes_in_30d"):
            if not Validation().check_if_is_number(self.post["plan_maxium_devices_changes_in_30d"]):
                return self.render_get_with_error("A quantidade máxima de troca de dispositivos deve ser um número")
        if self.post.get("plan_trial_duration_in_days"):
            if not Validation().check_if_is_number(self.post["plan_trial_duration_in_days"]):
                return self.render_get_with_error("A duração do plano trial em dias deve ser um número")

        if self.post.get("plan_app_can_be_offline_in_days"):
            if not Validation().check_if_is_number(self.post["plan_app_can_be_offline_in_days"]):
                return self.render_get_with_error("A duração do APP offline em dias deve ser um número")

        return self.render_get()
