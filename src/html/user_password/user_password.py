from python_web_frame.base_page import BasePage
from objects.User import User
from utils.utils.Http import Http


class UserPassword(BasePage):
    name = "TQS Cloud - Senha"
    public = True
    bypass = True
    admin = False

    def render_get(self):
        if not self.path.get("user_email"):
            return Http().redirect("user_login")
        user = self.load_user(self.path["user_email"])
        if not user:
            return Http().redirect("user_login")

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        html.esc("user_email_val", self.path["user_email"])
        if self.post.get("user_password"):
            html.esc("user_password_val", self.post["user_password"])
        return str(html)

    def render_post(self):
        if not self.path.get("user_email"):
            return Http().redirect("user_login")
        user = self.load_user(self.path["user_email"])
        if not user:
            return Http().redirect("user_login")

        if not self.post.get("user_password"):
            return self.render_get_with_error("Por favor informe a sua senha.")
        if not user.check_if_password_is_corrected(self.post["user_password"]):
            return self.render_get_with_error("Senha incorreta.")

        user.update_auth_token()
        return {"html": Http().redirect(""), "command": "login", "user_auth_token": user.user_auth_token}
