from python_web_frame.backoffice_page import BackofficePage
from utils.AWS.Dynamo import Dynamo
from utils.utils.Validation import Validation


class BackofficeOrdersHtml(BackofficePage):
    def run(self):
        order_user = self.load_user(self.post["search"])
        if not order_user:
            return {"success": ""}
        orders = Dynamo().query_user_orders(order_user.user_id)
        return {"success": self.list_html_backoffice_orders_table_rows(orders)}
