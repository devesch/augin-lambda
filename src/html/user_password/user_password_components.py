from utils.utils.ReadWrite import ReadWrite
from utils.AWS.Ses import Ses


class UserPasswordComponents:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserPasswordComponents, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def check_if_reset_password_was_sent(self, user_email, user_name, user_auth_token):
        html = ReadWrite().read_html("user_password/_codes/html_password_reset_email")
        html.esc("user_name_val", user_name)
        html.esc("user_auth_token", user_auth_token)
        return Ses().send_email(user_email, html, html, "Definir nova senha")
