from objects.AnalyticsNewUserRegistered import AnalyticsNewUserRegistered
from objects.BackofficeData import increase_backoffice_data_total_count
from objects.VerifyEmail import check_if_verify_email_expired
from utils.utils.EncodeDecode import EncodeDecode
from python_web_frame.user_page import UserPage
from utils.utils.Validation import Validation
from utils.utils.Generate import Generate
from utils.utils.JsonData import JsonData
from objects.User import User, load_user
from utils.AWS.Dynamo import Dynamo
from utils.utils.Http import Http


class UserRegister(UserPage):
    name = "Cadastro"
    public = True
    bypass = True
    admin = False

    def render_get(self):
        if not self.path.get("user_email"):
            return Http().redirect("user_login")
        if not self.path.get("verify_email"):
            return Http().redirect("user_login")
        if check_if_verify_email_expired(self.path["verify_email"]["created_at"]):
            return Http().redirect("user_login/?error_msg=" + EncodeDecode().encode_to_url("Seu código de verificação expirou, confirme seu email novamente."))
        if load_user(self.path["user_email"]):
            return Http().redirect("user_login")

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        html.esc("user_email_val", self.path["user_email"])
        if self.post.get("user_name"):
            html.esc("user_name_val", self.post["user_name"])
        if self.post.get("user_last_name"):
            html.esc("user_last_name_val", self.post["user_last_name"])
        if self.post.get("user_password"):
            html.esc("user_password_val", self.post["user_password"])

        if self.post.get("user_country"):
            user_country_alpha_2 = self.post["user_country"]
        else:
            ip_data = Http().get_request_ip_data(self.event.get_user_ip())
            if ip_data.get("country_code"):
                user_country_alpha_2 = ip_data.get("country_code").upper()
            else:
                user_country_alpha_2 = "BR"

        html.esc("html_user_country_options", self.list_html_user_country_options(user_country_alpha_2))

        if self.post.get("user_aggre_with_communication"):
            html.esc("user_aggre_with_communication_checked_val", "checked")
        if self.post.get("user_aggre_with_terms"):
            html.esc("user_aggre_with_terms_checked_val", "checked")
        if self.post.get("user_aggre_with_privacy_policy"):
            html.esc("user_aggre_with_privacy_policy_checked_val", "checked")
        if self.post.get("user_aggre_with_cookies_policy"):
            html.esc("user_aggre_with_cookies_policy_checked_val", "checked")
        return str(html)

    def render_post(self):
        if not self.path.get("user_email"):
            return Http().redirect("user_login")
        if not self.path.get("verify_email"):
            return Http().redirect("user_login")
        if check_if_verify_email_expired(self.path["verify_email"]["created_at"]):
            return Http().redirect("user_login/?error_msg=" + EncodeDecode().encode_to_url("Seu código de verificação expirou, confirme seu email novamente."))
        if load_user(self.path["user_email"]):
            return Http().redirect("user_login")

        if not self.post.get("user_name"):
            return self.render_get_with_error("Por favor informe um nome.")
        if not " " in self.post["user_name"]:
            return self.render_get_with_error("Por favor informe o nome completo.")
        if not self.post.get("user_password"):
            return self.render_get_with_error("Por favor informe uma Senha.")
        if not Validation().check_if_password(self.post["user_password"]):
            return self.render_get_with_error("A senha deve ter entre 8 e 45 caracteres.")
        if not self.post.get("user_country"):
            return self.render_get_with_error("Por favor selecione o seu país.")
        if not self.post["user_country"] in JsonData().get_country_data():
            del self.post["user_country"]
            return self.render_get_with_error("Por favor selecione um país válido.")
        if not self.post.get("user_aggre_with_terms"):
            return self.render_get_with_error("Por favor marque que está de acordo com os termos.")
        if not self.post.get("user_aggre_with_privacy_policy"):
            return self.render_get_with_error("Por favor marque que está de acordo com nossa política de privacidade.")
        if not self.post.get("user_aggre_with_cookies_policy"):
            return self.render_get_with_error("Por favor marque que está de acordo com nossa política de cookies.")

        user = User(Dynamo().get_next_user_id())
        user.user_email = self.path["user_email"]
        user.user_name = self.post["user_name"].title().strip()
        user.user_first_three_letters_name = user.user_name[:3]
        user.user_address_data["user_country"] = self.post["user_country"].upper()
        if self.post["user_country"].upper() != "BR":
            user.user_client_type = "international"
        user.user_status = "created"
        user.user_ip = self.event.get_user_ip()

        user_dicts_folder = user.create_new_folder("", is_user_root_folder=True)
        user_shared_dicts_folder = user.create_new_folder("", is_user_root_folder=True)
        user.user_dicts_folder_id = user_dicts_folder["folder_id"]
        user.user_shared_dicts_folder_id = user_shared_dicts_folder["folder_id"]

        user.update_cart_currency()
        increase_backoffice_data_total_count("user")

        Dynamo().put_entity(user.__dict__)
        user.update_password(self.post["user_password"], Generate().generate_salt(9))
        user.update_auth_token()

        Dynamo().put_entity(AnalyticsNewUserRegistered().__dict__)

        all_users_verify_email = Dynamo().query_users_verify_email(self.path["user_email"])
        for user_verify_email in all_users_verify_email:
            Dynamo().delete_entity(user_verify_email)
        return {"html": Http().redirect("panel_your_plan"), "command": "login", "user_auth_token": user.user_auth_token}
