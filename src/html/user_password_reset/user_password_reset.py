from python_web_frame.user_page import UserPage
from objects.User import User
from utils.AWS.Dynamo import Dynamo
from utils.utils.Http import Http
from utils.utils.Validation import Validation
from utils.utils.Generate import Generate


class UserPasswordReset(UserPage):
    name = "Resetar Senha"
    public = True
    bypass = True
    admin = False

    def render_get(self):
        if not self.path.get("user_auth_token"):
            return Http().redirect("user_login")
        user = User("")
        user.load_information_with_auth_token(self.path["user_auth_token"])
        if user.user_status != "created":
            return Http().redirect("user_login")

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        html.esc("user_email_val", user.user_email)
        if self.post.get("user_password"):
            html.esc("user_password_val", self.post["user_password"])
        return str(html)

    def render_post(self):
        if not self.path.get("user_auth_token"):
            return Http().redirect("user_login")
        user = User("")
        user.load_information_with_auth_token(self.path["user_auth_token"])
        if user.user_status != "created":
            return Http().redirect("user_login")

        if not self.post.get("user_password"):
            return self.render_get_with_error("Por favor informe uma senha.")
        if not Validation().check_if_password(self.post["user_password"]):
            return self.render_get_with_error("A senha deve ter entre 8 e 45 caracteres.")

        user.update_password(self.post["user_password"], Generate().generate_salt(9))
        Dynamo().put_entity(user.__dict__)
        user.update_auth_token()
        return {"html": Http().redirect("panel_your_plan"), "command": "login", "user_auth_token": user.user_auth_token}
