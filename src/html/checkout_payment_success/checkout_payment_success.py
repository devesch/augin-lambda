from python_web_frame.checkout_page import CheckoutPage
from utils.utils.Http import Http
from objects.Order import generate_order_short_id


class CheckoutPaymentSuccess(CheckoutPage):
    name = "Checkout - Pagamento realizado com sucesso"

    def render_get(self):
        if not self.path.get("order_id"):
            return Http().redirect("panel_your_plan")

        html = super().parse_html()
        html.esc("order_short_id_val", generate_order_short_id(self.path["order_id"]))
        html.esc("order_id_val", self.path["order_id"])

        if self.path["order"]["order_payment_method"] == "boleto":
            html.esc("order_is_boleto_val", "true")
        else:
            html.esc("order_is_boleto_val", "false")
        return str(html)

    def render_post(self):
        return self.render_get()
