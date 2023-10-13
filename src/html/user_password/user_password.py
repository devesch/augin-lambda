from python_web_frame.user_page import UserPage
from utils.utils.Http import Http
from objects.User import load_user


class UserPassword(UserPage):
    name = "Senha"
    public = True
    bypass = True
    admin = False

    def render_get(self):
        if not self.path.get("user_email"):
            return Http().redirect("user_login")
        user = load_user(self.path["user_email"])
        if not user:
            return Http().redirect("user_login")

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)

        self.path["render_captcha"] = self.check_if_captcha_should_be_rendered()
        if self.path.get("render_captcha"):
            html.esc("html_captcha_verification", self.show_html_captcha_verification())

        html.esc("user_email_val", self.path["user_email"])
        if self.post.get("user_password"):
            html.esc("user_password_val", self.post["user_password"])
        return str(html)

    def render_post(self):
        if not self.path.get("user_email"):
            return Http().redirect("user_login")
        user = load_user(self.path["user_email"])
        if not user:
            return Http().redirect("user_login")

        self.path["render_captcha"] = self.check_if_captcha_should_be_rendered()
        if self.path.get("render_captcha"):
            if not self.post.get("h-captcha-response"):
                return self.render_get_with_error("Por favor preencha o captcha")

            captacha_response = Http().verify_hcaptcha(self.post["h-captcha-response"], self.event.get_user_ip())
            if not captacha_response["success"]:
                return self.render_get_with_error("Captacha inválido")

        if not self.post.get("user_password"):
            return self.render_get_with_error("Por favor informe a sua senha.")
        if not user.check_if_password_is_corrected(self.post["user_password"]):
            return self.render_get_with_error("Senha incorreta.")

        user.update_auth_token()
        return {"html": Http().redirect("panel_your_plan"), "command": "login", "user_auth_token": user.user_auth_token}

    def check_if_captcha_should_be_rendered(self):
        if "incorreta" in self.error_msg.lower() or "captcha" in self.error_msg.lower():
            return True
        return False
