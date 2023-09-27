from python_web_frame.panel_page import PanelPage


class PanelExploreProjectUserDictsHtml(PanelPage):
    def run(self):
        user_plan = None
        if self.user:
            user_plan = self.user.get_user_actual_plan()
        return {"success": self.list_html_user_folder_rows(user_plan, self.post.get("folder_id"), self.post.get("model_html"))}
