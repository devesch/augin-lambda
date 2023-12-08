from python_web_frame.backoffice_page import BackofficePage
from utils.utils.Http import Http
from utils.utils.ReadWrite import ReadWrite


class BackofficeOrder(BackofficePage):
    name = "Backoffice - Pagamento"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        if not self.path.get("order"):
            return Http().redirect("backoffice_orders")

        html = super().parse_html()
        html.esc("html_key_val_section", self.list_html_key_val_section(self.path["order"]))
        html.esc("order_id_val", self.path["order"]["order_id"])

        if self.path["order"]["order_status"] == "paid":
            html.esc("html_refund_order_button", self.show_html_refund_order_button())
            if self.path["order"]["order_nfse_status"] != "issued":
                html.esc("html_issue_order_nfse_button", self.show_html_issue_order_nfse_button())

        return str(html)

    def render_post(self):
        return self.render_get()

    def show_html_issue_order_nfse_button(self):
        return str(ReadWrite().read_html("backoffice_order/_codes/html_issue_order_nfse_button"))

    def show_html_refund_order_button(self):
        return str(ReadWrite().read_html("backoffice_order/_codes/html_refund_order_button"))
