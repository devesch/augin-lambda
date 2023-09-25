from python_web_frame.checkout_page import CheckoutPage
from utils.utils.Http import Http
from objects.Order import generate_order_short_id


class CheckoutPaymentSuccess(CheckoutPage):
    name = "Checkout - Pagamento Realizado com Sucesso"

    def render_get(self):
        if not self.path.get("order_id"):
            return Http().redirect("panel_your_plan")

        html = super().parse_html()

        html.esc("order_short_id_val", generate_order_short_id(self.path["order_id"]))
        html.esc("order_id_val", self.path["order_id"])
        return str(html)

    def render_post(self):
        return self.render_get()