from python_web_frame.panel_page import PanelPage
from utils.Config import lambda_constants
from objects.Plan import translate_reference_tracker


class PanelYourPlan(PanelPage):
    name = "Painel - Seu Plano"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        html.esc("user_name_val", self.user.user_name.title())
        self.user.update_user_plan()
        html.esc("plan_name_val", self.user.user_plan["plan_name_" + self.lang])
        html.esc("plan_name_val", self.user.user_plan["plan_name_" + self.lang])

        html.esc("plan_maxium_model_size_in_mbs_val", self.user.user_plan["plan_maxium_model_size_in_mbs"])
        html.esc("plan_cloud_space_in_mbs_val", self.user.user_plan["plan_cloud_space_in_mbs"])

        if self.user.user_plan["plan_share_files"]:
            html.esc("plan_share_files_val", self.translate("Sim"))
        else:
            html.esc("plan_share_files_val", self.translate("Não"))

        html.esc("plan_reference_tracker_val", self.translate(translate_reference_tracker(self.user.user_plan["plan_reference_tracker"])))

        if self.user.user_plan["plan_maxium_federated_size_in_mbs"] == "0":
            html.esc("plan_maxium_federated_size_in_mbs_val", self.translate("Não"))
        else:
            html.esc("plan_maxium_federated_size_in_mbs_val", self.user.user_plan["plan_maxium_federated_size_in_mbs"] + " Mb")

        html.esc("plan_maxium_devices_available_val", self.user.user_plan["plan_maxium_devices_available"])
        if self.user.user_plan["plan_download_files"]:
            html.esc("plan_download_files_val", self.translate("Sim"))
        else:
            html.esc("plan_download_files_val", self.translate("Não"))

        return str(html)

    def render_post(self):
        return self.render_get()
