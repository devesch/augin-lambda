from python_web_frame.user_page import UserPage
from utils.utils.Http import Http
from utils.utils.Validation import Validation
from utils.utils.EncodeDecode import EncodeDecode


class UserEmailChangedConfirm(UserPage):
    name = "Confirmação de troca de email"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get("")
