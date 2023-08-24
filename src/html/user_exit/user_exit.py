from python_web_frame.base_page import BasePage
from utils.utils.Http import Http


class UserExit(BasePage):
    name = "TQS Cloud - Sair"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        if self.user:
            if self.user.user_is_tqs:
                return {"html": Http().redirect_to_another_url("https://www.tqs.com.br/account/logout"), "command": "logout", "user_auth_token": None}
        return {"html": Http().redirect(""), "command": "logout", "user_auth_token": None}

    def render_post(self):
        return self.render_get()
