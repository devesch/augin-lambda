from python_web_frame.backoffice_page import BackofficePage
from utils.utils.Date import Date


class BackofficeUser(BackofficePage):
    name = "Backoffice - Usuário"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        user = self.load_user(self.path["user_id"])
        user = user.__dict__

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

        return str(html)

    def render_post(self):
        return self.render_get()
