from python_web_frame.panel_page import PanelPage


class PanelExploreProjectsModalMoveUserDictsHtml(PanelPage):
    def run(self):
        return {"success": self.list_html_user_folder_rows(self.post.get("folder_id"), model_html="move")}
