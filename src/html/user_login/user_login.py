from python_web_frame.user_page import UserPage
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.Validation import Validation
from utils.AWS.Dynamo import Dynamo
from utils.utils.Http import Http
from objects.User import load_user
from objects.ValidEmail import ValidEmail


class UserLogin(UserPage):
    name = "Login"
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

        valid_email = Dynamo().get_valid_email(self.post["user_email"])
        if not valid_email:
            if not Validation().check_if_email_valid_in_zerobounce(self.post["user_email"]):
                return self.render_get_with_error("Email inválido por favor informe outro email.")
            else:
                valid_email = ValidEmail(self.post["user_email"]).__dict__
                Dynamo().put_entity(valid_email)

        user = load_user(self.post["user_email"])
        if user:
            return Http().redirect("user_password/?user_encoded_email=" + EncodeDecode().encode_to_b64(self.post["user_email"]))
        else:
            self.generate_and_send_email_verification_code()
            return Http().redirect("user_verify_email/?user_encoded_email=" + EncodeDecode().encode_to_b64(self.post["user_email"]))
