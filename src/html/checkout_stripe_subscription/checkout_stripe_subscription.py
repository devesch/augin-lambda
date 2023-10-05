from python_web_frame.checkout_page import CheckoutPage
from python_web_frame.controllers.stripe_controller import stripe_token
from utils.AWS.Dynamo import Dynamo
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
            return Http().redirect("checkout_upgrade_your_plan")

        if self.path.get("plan_trial"):
            if not self.path["plan"]["plan_has_trial"]:
                return Http().redirect("checkout_upgrade_your_plan")
            trial_plan_version = Dynamo().get_plan(self.path["plan"]["plan_id"] + "-trial")
            if trial_plan_version and self.path["plan"]["plan_id"] + "-trial" not in self.user.user_used_trials:
                self.user.active_trial_plan(trial_plan_version)
                return Http().redirect("panel_your_plan")

        html = super().parse_html()
        html.esc("user_name_val", self.user.user_name)
        html.esc("user_email_val", self.user.user_email)
        html.esc("plan_name_val", self.path["plan"]["plan_name_" + self.lang])

        plan_discounted_price = None
        discount_value = None
        if self.user.user_cart_coupon_code:
            html.esc("html_add_or_remove_coupon_button", self.show_html_remove_coupon_button())
            plan_discounted_price, discount_value = self.user.generate_plan_price_with_coupon_discount(self.path["plan"], self.path["plan_recurrency"], self.user.user_cart_currency)
        else:
            html.esc("html_add_or_remove_coupon_button", self.show_html_add_coupon_button())

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

        if plan_discounted_price and discount_value:
            html.esc("discount_value_val", StrFormat().format_to_money(discount_value, self.user.user_cart_currency))
            html.esc("plan_discounted_price_val", StrFormat().format_to_money(plan_discounted_price, self.user.user_cart_currency))
        else:
            html.esc("coupon_discount_visibility_val", "display:none;")

        html.esc("user_cart_currency_symbol", StrFormat().format_currency_to_symbol(self.user.user_cart_currency))
        html.esc("stripe_token_val", stripe_token)
        html.esc("plan_id_val", self.path["plan"]["plan_id"])
        html.esc("plan_recurrency_val", self.path["plan_recurrency"])
        if self.user.user_cart_coupon_code:
            html.esc("user_cart_coupon_code_val", self.user.user_cart_coupon_code)

        return str(html)

    def render_post(self):
        return self.render_get()
