from python_web_frame.base_page import BasePage


class Error(BasePage):
    name = "TQS Cloud - Estamos com dificuldades"
    public = True
    bypass = False

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        return str(html)

    def render_post(self):
        return self.render_get()
