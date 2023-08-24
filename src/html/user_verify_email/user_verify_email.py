from python_web_frame.user_page import UserPage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Http import Http
from utils.utils.EncodeDecode import EncodeDecode


class UserVerifyEmail(UserPage):
    name = "Confirmação de Email"
    public = True
    bypass = True
    admin = False

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        html.esc("user_email_val", self.path["user_email"])
        self.check_error_msg(html, self.error_msg)
        if self.post:
            html.esc("focus_input_id_val", "verify_email_code_6")
            for param in self.post:
                html.esc(param + "_val", self.post[param])
        else:
            html.esc("focus_input_id_val", "verify_email_code_1")
        return str(html)

    def render_post(self):
        self.post["verify_email_code"] = self.generate_verification_code()
        if not self.post.get("verify_email_code"):
            return self.render_get_with_error("Por favor informe um código de verificação de 6 dígitos")
        verify_email = Dynamo().get_verify_email(self.path["user_email"], self.post["verify_email_code"])
        if not verify_email:
            return self.render_get_with_error("Código de verificação inválido.")
        if self.check_if_verify_email_expired(verify_email["created_at"]):
            return self.render_get_with_error("Código de verificação expirado.")
        return Http().redirect("user_register/?user_encoded_email=" + EncodeDecode().encode_to_b64(self.path["user_email"]) + "&verify_email_code=" + self.post["verify_email_code"])
