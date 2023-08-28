from python_web_frame.base_page import BasePage


class default_lambda_page_name_val(BasePage):
    menu = "backoffice_menu"

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get()
