from python_web_frame.checkout_page import CheckoutPage
from python_web_frame.controllers.stripe_controller import stripe_token
from utils.utils.Http import Http
from utils.utils.StrFormat import StrFormat


class CheckoutStripeSubscription(CheckoutPage):
    name = "Painel - Confirme a compra do seu plano"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        if not self.path["plan_recurrency"]:
            return Http().redirect("panel_your_plan")
        if self.path["plan_recurrency"] not in ["monthly", "annually"]:
            return Http().redirect("panel_your_plan")
        if not self.path["plan"]:
            return Http().redirect("panel_your_plan")

        if (self.path["plan_recurrency"] == "monthly" and not self.path["plan"]["plan_available_monthly"]) or (self.path["plan_recurrency"] == "annually" and not self.path["plan"]["plan_available_annually"]):
            return Http().redirect("panel_your_plan")

        html = super().parse_html()
        html.esc("user_name_val", self.user.user_name)
        html.esc("user_email_val", self.user.user_email)
        html.esc("plan_name_val", self.path["plan"]["plan_name_" + self.lang])

        if self.path["plan_recurrency"] == "annually":
            html.esc("plan_recurrency_phrase_val", self.translate("ano"))
            if self.user.user_cart_currency == "brl":
                html.esc("plan_price_val", StrFormat().format_to_money(self.path["plan"]["plan_price_annually_brl_actual"], self.user.user_cart_currency))
            if self.user.user_cart_currency == "usd":
                html.esc("plan_price_val", StrFormat().format_to_money(self.path["plan"]["plan_price_annually_usd_actual"], self.user.user_cart_currency))

        elif self.path["plan_recurrency"] == "monthly":
            html.esc("plan_recurrency_phrase_val", self.translate("mês"))
            if self.user.user_cart_currency == "brl":
                html.esc("plan_price_val", StrFormat().format_to_money(self.path["plan"]["plan_price_monthly_brl_actual"], self.user.user_cart_currency))
            if self.user.user_cart_currency == "usd":
                html.esc("plan_price_val", StrFormat().format_to_money(self.path["plan"]["plan_price_monthly_usd_actual"], self.user.user_cart_currency))

        html.esc("user_cart_currency_symbol", StrFormat().format_currency_to_symbol(self.user.user_cart_currency))
        html.esc("stripe_token_val", stripe_token)
        html.esc("plan_id_val", self.path["plan"]["plan_id"])
        html.esc("plan_recurrency_val", self.path["plan_recurrency"])
        return str(html)

    def render_post(self):
        return self.render_get()
