﻿from python_web_frame.user_page import UserPage
from objects.User import load_user


class UserEmailChangedConfirm(UserPage):
    name = "Confirmação de troca de email"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        user = load_user(self.path["user_auth_token"])
        user.update_attribute("user_email", self.path["new_user_email"])
        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get()
