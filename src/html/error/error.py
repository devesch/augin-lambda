from python_web_frame.base_page import BasePage
from utils.utils.ReadWrite import ReadWrite


class Error(BasePage):
    name = "Estamos com dificuldades"
    public = True
    bypass = False

    def render_get(self):
        html = super().parse_html()
        if self.path and self.path.get("error"):
            html.esc("error_title_val", self.translate("Não foi possível encontrar arquivo"))
            html.esc("html_error_message", self.show_html_error_message(self.path["error"]))
        else:
            html.esc("error_title_val", self.translate("Problema temporário"))
            html.esc("html_error_message", str(ReadWrite().read_html("error/_codes/html_default_error_message")))
        self.check_error_msg(html, self.error_msg)
        return str(html)

    def render_post(self):
        return self.render_get()

    def show_html_error_message(self, error_msg):
        html = ReadWrite().read_html("error/_codes/html_custom_error_message")
        html.esc("custom_error_message_val", self.translate(error_msg))
        return str(html)
