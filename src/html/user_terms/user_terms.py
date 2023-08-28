﻿from python_web_frame.user_page import UserPage


class UserTerms(UserPage):
    name = "Termos de Uso"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get()
