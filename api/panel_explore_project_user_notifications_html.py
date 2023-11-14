from python_web_frame.panel_page import PanelPage
from utils.AWS.Dynamo import Dynamo


class PanelExploreProjectUserNotificationsHtml(PanelPage):
    def run(self):
        user_notifications = Dynamo().query_user_notifications(self.user.user_id)
        return {"success": self.list_html_notifications_li_items(user_notifications)}
