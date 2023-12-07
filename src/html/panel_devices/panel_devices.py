from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.model_controller import ModelController
from objects.UserDevice import generate_connected_and_disconnected_devices, generate_disconnected_devices_in_last_30d
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation
from utils.Config import lambda_constants


class PanelDevices(PanelPage):
    name = "Painel - Dispositivos"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        user_plan = self.user.get_user_actual_plan()
        html.esc("html_upgrade_button", self.show_html_upgrade_button(user_plan))
        html.esc("html_notifications_button", self.show_html_notifications_button())
        if user_plan["plan_id"] == lambda_constants["free_plan_id"]:
            html.esc("make_and_upgrade_phrase_val", self.translate("Faça um upgrade para aumentar esse limite."))

        html.esc("plan_maxium_devices_available_val", user_plan["plan_maxium_devices_available"])
        html.esc("plan_maxium_devices_changes_in_30d_val", user_plan["plan_maxium_devices_changes_in_30d"])

        user_devices = Dynamo().query_all_user_devices(self.user.user_id)
        connected_devices, disconnected_devices = generate_connected_and_disconnected_devices(user_devices)
        disconnected_devices_in_last_30d = generate_disconnected_devices_in_last_30d(disconnected_devices)

        html.esc("lenght_of_connected_devices_val", len(connected_devices))
        html.esc("lenght_of_disconnected_devices_in_last_30d_val", len(disconnected_devices_in_last_30d))

        html.esc("html_user_devices_thumbs", self.list_html_user_devices_thumbs(connected_devices, disconnected_devices_in_last_30d, user_plan["plan_maxium_devices_changes_in_30d"]))
        html.esc("html_user_available_devices_thumbs", self.list_html_user_available_devices_thumbs(connected_devices, user_plan["plan_maxium_devices_available"]))
        return str(html)

    def render_post(self):
        return self.render_get()
