from python_web_frame.panel_page import PanelPage
from utils.utils.Validation import Validation
from utils.utils.Generate import Generate
from utils.utils.ReadWrite import ReadWrite
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Ses import Ses


class PanelUserNewPassword(PanelPage):
    name = "Painel - Nova Senha do Usuário"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        html.esc("user_email_val", self.user.user_email)
        if self.post.get("user_current_password"):
            html.esc("user_current_password_val", self.post["user_current_password"])
        if self.post.get("user_password"):
            html.esc("user_password_val", self.post["user_password"])
        return str(html)

    def render_post(self):
        if not self.post.get("user_current_password"):
            return self.render_get_with_error("Por favor informe a senha atual.")
        if not self.user.check_if_password_is_corrected(self.post["user_current_password"]):
            return self.render_get_with_error("A senha atual está incorreta.")
        if not self.post.get("user_password"):
            return self.render_get_with_error("Por favor informe uma senha.")
        if not Validation().check_if_password(self.post["user_password"]):
            return self.render_get_with_error("A senha deve ter entre 8 e 45 caracteres.")

        self.user.update_password(self.post["user_password"], Generate().generate_salt(9))
        self.user.user_ip = self.event.get_user_ip()
        Dynamo().put_entity(self.user.__dict__)
        user_password_modified_email = self.generate_user_password_modified_email(self.user.user_name)
        self.user.clear_all_auth_tokens()
        Ses().send_email(self.user.user_email, body_html=user_password_modified_email, body_text=user_password_modified_email, subject_data="Augin - Sua senha foi alterada")
        return {"html": self.utils.redirect("home"), "command": "logout", "user_auth_token": None}

    def generate_user_password_modified_email(self, user_name):
        html = ReadWrite().read_html("panel_user_new_password/_codes/html_password_modified_email")
        html.esc("user_name_val", user_name)
        return str(html)
