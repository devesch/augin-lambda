from python_web_frame.checkout_page import CheckoutPage
from utils.Config import lambda_constants
from objects.Plan import translate_reference_tracker
from utils.utils.ReadWrite import ReadWrite
from utils.utils.StrFormat import StrFormat
from utils.AWS.Dynamo import Dynamo


class CheckoutStripeSubscription(CheckoutPage):
    name = "Painel - Confirme o seu plano"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        return str(html)

    def render_post(self):
        return self.render_get()
