from python_web_frame.base_page import BasePage
from objects.User import User
from utils.AWS.Dynamo import Dynamo
from utils.utils.Http import Http
from utils.utils.Validation import Validation
from utils.utils.Generate import Generate


class UserRegister(BasePage):
    name = "TQS Cloud - Cadastro"
    public = True
    bypass = True
    admin = False

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)

        if self.post.get("user_email"):
            html.esc("user_email_val", self.post["user_email"])
        if self.post.get("user_name"):
            html.esc("user_name_val", self.post["user_name"])
        if self.post.get("user_password"):
            html.esc("user_password_val", self.post["user_password"])
        if self.post.get("user_password_confirm"):
            html.esc("user_password_confirm_val", self.post["user_password_confirm"])
        if self.post.get("user_aggre_with_terms"):
            html.esc("user_aggre_with_terms_checked_val", "checked")
        return str(html)

    def render_post(self):

        if not self.post.get("user_aggre_with_terms"):
            return self.render_get_with_error("Por favor marque que está de acordo com os termos.")
        if not self.post.get("user_email"):
            return self.render_get_with_error("Por favor informe um Email.")
        if not self.post.get("user_password"):
            return self.render_get_with_error("Por favor informe uma senha.")
        if not self.post.get("user_password_confirm"):
            return self.render_get_with_error("Por favor confirme sua senha.")
        if not Validation().check_if_password(self.post["user_password"]):
            return self.render_get_with_error("A senha deve ter entre 8 e 45 caracteres.")
        if self.post["user_password"] != self.post["user_password_confirm"]:
            return self.render_get_with_error("As senhas informadas devem coincidir.")

        user = self.load_user(self.post["user_email"])
        if user:
            return self.render_get_with_error("Já existe uma conta com este email.")

        user = User(self.path["user_email"])
        user.user_status = "created"
        user.user_name = self.post["user_name"].title()
        Dynamo().put_entity(user.__dict__)
        user.update_password(self.post["user_password"], Generate().generate_salt(9))
        user.update_auth_token()

        return {"html": Http().redirect("/home")}
