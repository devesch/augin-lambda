from python_web_frame.base_page import BasePage
from utils.utils.Http import Http
from utils.utils.Validation import Validation
from utils.utils.EncodeDecode import EncodeDecode


class UserLogin(BasePage):
    name = "TQS Cloud - Entrar"
    public = True
    bypass = True
    admin = False

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        if self.post.get("user_email"):
            html.esc("user_email_val", self.post["user_email"])
        return str(html)

    def render_post(self):
        if not self.post.get("user_email"):
            return self.render_get_with_error("Informe um email.")
        if not Validation().check_if_email(self.post["user_email"]):
            return self.render_get_with_error("Email inválido.")

        user = self.load_user(self.post["user_email"])
        if user:
            return Http().redirect("user_password/?user_encoded_email=" + EncodeDecode().encode_to_b64(self.post["user_email"]))
        else:
            return Http().redirect("user_register/?user_encoded_email=" + EncodeDecode().encode_to_b64(self.post["user_email"]))
