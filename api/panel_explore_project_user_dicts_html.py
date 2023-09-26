from python_web_frame.panel_page import PanelPage


class PanelExploreProjectUserDictsHtml(PanelPage):
    def run(self):
        return {"success": self.list_html_user_folder_rows(self.user.get_user_actual_plan(), self.post.get("folder_id"), self.post.get("model_html"))}
