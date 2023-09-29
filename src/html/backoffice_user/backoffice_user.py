from python_web_frame.backoffice_page import BackofficePage
from utils.utils.Validation import Validation
from utils.AWS.Dynamo import Dynamo
import json


class BackofficeUser(BackofficePage):
    name = "Backoffice - Usuário"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        return str(html)

    def render_post(self):
        return self.render_get()
