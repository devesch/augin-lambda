﻿from python_web_frame.base_page import BasePage
from utils.utils.Http import Http


class Home(BasePage):
    name = "Augin"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        if self.post.get("select_translation"):
            if not self.post.get("user_url"):
                self.post["user_url"] = ""
            if self.post["select_translation"] not in ("pt", "es", "en"):
                self.post["select_translation"] = "en"
            if self.user:
                self.user.update_attribute("user_lang", self.post["select_translation"])
            return {"html": Http().redirect(self.post["user_url"].replace("/", "/?")), "command": "change_lang", "user_lang": self.post["select_translation"]}
        if self.post.get("change_cookie_policy"):
            cookie_policy = {"tawk": "accepted", "mouseflow": "accepted"}
            if self.post["cookie_policy"] != "accept":
                if not self.post.get("tawk"):
                    cookie_policy["tawk"] = "deny"
                if not self.post.get("mouseflow"):
                    cookie_policy["mouseflow"] = "deny"
            return {"html": Http().redirect(self.post["user_url"].replace("/", "/?")), "command": "change_cookie_policy", "cookie_policy": cookie_policy}
        return self.render_get()
