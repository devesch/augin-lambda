from python_web_frame.backoffice_page import BackofficePage


class BackofficeLoginAsAnotherUser(BackofficePage):
    name = "Backoffice"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get()
