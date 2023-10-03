from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.model_controller import ModelController
from utils.AWS.Dynamo import Dynamo
from utils.utils.Http import Http
from utils.utils.Date import Date
from utils.Config import lambda_constants
import time


class PanelDevices(PanelPage):
    name = "Painel - Dispositivos"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        user_plan = self.user.get_user_actual_plan()
        html.esc("html_upgrade_button", self.show_html_upgrade_button(user_plan))
        html.esc("plan_maxium_model_size_in_mbs_val", user_plan["plan_maxium_model_size_in_mbs"])
        if user_plan["plan_id"] == lambda_constants["free_plan_id"]:
            html.esc("make_and_upgrade_phrase_val", self.translate("Faça um upgrade para aumentar esse limite."))

        html.esc("plan_maxium_devices_available_val", user_plan["plan_maxium_devices_available"])
        html.esc("plan_maxium_devices_changes_in_30d_val", user_plan["plan_maxium_devices_changes_in_30d"])
        return str(html)

    def render_post(self):
        return self.render_get()
