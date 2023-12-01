from python_web_frame.user_page import UserPage
from utils.AWS.Ses import Ses
from utils.utils.ReadWrite import ReadWrite
from utils.utils.EncodeDecode import EncodeDecode
from objects.User import load_user


class UserSendResetPasswordEmail(UserPage):
    def run(self):
        if not self.post.get("user_email"):
            return {"error": "Nenhum email enviado no formulário."}
        self.user = load_user(self.post["user_email"])
        if not self.user:
            return {"error": "Usuário inexistente."}
        self.user.update_auth_token()
        if self.check_if_reset_password_was_sent(self.user.user_email, self.user.user_name, self.user.user_auth_token):
            return {"success": "Email de reset de senha enviado com sucesso."}
        else:
            return {"error": "Não foi possível enviar o email, entre em contato com o suporte."}

    def check_if_reset_password_was_sent(self, user_email, user_name, user_auth_token):
        try:
            html = ReadWrite().read_html("main/emails/html_password_reset_email")
            html.esc("user_name_val", user_name)
            html.esc("user_encoded_email_val", EncodeDecode().encode_to_b64(user_email))
            html.esc("user_auth_token_val", user_auth_token)
            Ses().send_email(user_email, body_html=str(html), body_text=str(html), subject_data=self.translate("Augin - Definir nova senha"))
            return True
        except:
            return False
