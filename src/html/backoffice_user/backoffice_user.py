from objects.UserDevice import disconnect_device, generate_connected_and_disconnected_devices
from objects.User import load_user
from python_web_frame.backoffice_page import BackofficePage
from utils.utils.StrFormat import StrFormat
from utils.utils.Date import Date
from utils.AWS.Dynamo import Dynamo
import time


class BackofficeUser(BackofficePage):
    name = "Backoffice - Usuário"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        user = load_user(self.path["user_id"])
        user = user.__dict__

        html.esc("user_id_val", user["user_id"])
        html.esc("user_email_val", user["user_email"])
        html.esc("user_name_val", user["user_name"])
        html.esc("user_phone_val", StrFormat().format_to_phone(user["user_phone"]))
        if user["user_client_type"] == "physical":
            html.esc("user_cpf_or_cnpj_val", StrFormat().format_to_cpf(user["user_cpf"]))
        if user["user_client_type"] == "company":
            html.esc("user_cpf_or_cnpj_val", StrFormat().format_to_cpf(user["user_cnpj"]))
        html.esc("user_client_type_val", user["user_client_type"])
        html.esc("user_subscription_status_val", user["user_subscription_status"])
        html.esc("user_plan_id_val", user["user_plan_id"])
        if user["user_plan_id"]:
            user_plan = Dynamo().get_plan(user["user_plan_id"])
            html.esc("user_plan_name_val", user_plan["plan_name_pt"])

        html.esc("user_last_login_at_val", Date().format_unixtime_to_br_date(user["user_last_login_at"]))
        html.esc("user_cart_currency_val", StrFormat().format_currency_to_symbol(user["user_cart_currency"]))
        html.esc("user_country_val", user["user_address_data"]["user_country"])
        html.esc("user_auth_token_val", user["user_auth_token"])

        return str(html)

    def render_post(self):
        if self.post.get("command"):
            if self.post["command"] == "disconnect_devices":
                user = load_user(self.path["user_id"])
                user_devices = Dynamo().query_all_user_devices(user.user_id)
                connected_devices, disconnected_devices = generate_connected_and_disconnected_devices(user_devices)
                for connected_device in connected_devices:
                    disconnect_device(connected_device, disconnection_at=str(time.time() - 2800000))
                return self.render_get_with_error("Todos os dispositivos que estavam conectados foram desconetados com sucesso")

            if self.post["command"] == "reset_user_used_trials":
                user = load_user(self.path["user_id"])
                user.reset_user_used_trials()
                return self.render_get_with_error("Planos trials já utilizados resetados")
        return self.render_get()
