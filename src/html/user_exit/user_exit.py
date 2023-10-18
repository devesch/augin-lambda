from python_web_frame.base_page import BasePage
from utils.utils.Http import Http
from utils.AWS.Dynamo import Dynamo


class UserExit(BasePage):
    name = "Sair"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        auth_token = Dynamo().get_auth_token(self.event.get_user_auth_token())
        if auth_token:
            Dynamo().delete_entity(auth_token)
        return {"html": Http().redirect(""), "command": "logout", "user_auth_token": None}

    def render_post(self):
        return self.render_get()
