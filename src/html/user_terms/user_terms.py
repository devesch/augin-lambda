from python_web_frame.base_page import BasePage


class UserTerms(BasePage):
    name = "TQS Cloud - Termos de Uso"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get()
