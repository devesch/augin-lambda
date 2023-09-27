﻿from python_web_frame.panel_page import PanelPage
from utils.utils.Http import Http


class ViewFolder(PanelPage):
    name = "Visualizar Pasta"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        if not self.path.get("folder"):
            return Http().redirect("user_login")

        if self.user:
            return Http().redirect("panel_shared_project/?folder_id=" + self.path["folder"]["folder_id"])

        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get()