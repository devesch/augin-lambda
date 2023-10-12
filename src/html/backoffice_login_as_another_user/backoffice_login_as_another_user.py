from python_web_frame.backoffice_page import BackofficePage
from utils.utils.Http import Http
from objects.User import load_user


class BackofficeLoginAsAnotherUser(BackofficePage):
    name = "Backoffice"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        user = load_user(self.path["user_auth_token"])
        return {"html": Http().redirect("panel_your_plan"), "command": "login", "user_auth_token": user.user_auth_token}

    def render_post(self):
        return self.render_get()
