from python_web_frame.panel_page import PanelPage


class PanelExploreProject(PanelPage):
    name = "Painel - Explorar Projetos"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get()