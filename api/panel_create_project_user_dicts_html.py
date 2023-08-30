from python_web_frame.panel_page import PanelPage


class PanelCreateProjectUserDictsHtml(PanelPage):
    def run(self):
        return {"success": self.list_html_user_folder_rows()}
