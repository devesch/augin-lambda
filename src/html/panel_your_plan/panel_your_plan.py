from python_web_frame.panel_page import PanelPage


class PanelYourPlan(PanelPage):
    name = "Painel - Seu Plano"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get()
