from python_web_frame.backoffice_page import BackofficePage


class BackofficeHome(BackofficePage):
    name = "Backoffice - Home"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get()
