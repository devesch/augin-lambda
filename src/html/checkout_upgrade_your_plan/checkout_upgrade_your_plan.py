from python_web_frame.checkout_page import CheckoutPage
from utils.Config import lambda_constants
from objects.Plan import translate_reference_tracker, generate_plans_hierarchy
from utils.utils.ReadWrite import ReadWrite
from utils.utils.StrFormat import StrFormat
from utils.AWS.Dynamo import Dynamo


class CheckoutUpgradeYourPlan(CheckoutPage):
    name = "Painel - Melhore Seu Plano"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        user_subscription = None
        if self.user.user_subscription_id:
            user_subscription = Dynamo().get_subscription(self.user.user_subscription_id)
        user_plan = self.user.get_user_actual_plan()

        html = super().parse_html()
        html.esc("html_upgrade_button", self.show_html_upgrade_button(user_plan))
        html.esc("user_name_val", self.user.user_name.title())
        html.esc("plan_name_val", user_plan["plan_name_" + self.lang])
        purchasable_plans = Dynamo().query_purchasable_plans()
        plans_hierarchy = generate_plans_hierarchy(purchasable_plans)
        html.esc("html_monthly_plans_thumbs", self.list_html_plans_thumbs(purchasable_plans, "monthly", user_subscription, plans_hierarchy))
        html.esc("html_annually_plans_thumbs", self.list_html_plans_thumbs(purchasable_plans, "annually", user_subscription, plans_hierarchy))
        return str(html)

    def render_post(self):
        return self.render_get()

    def list_html_plans_thumbs(self, purchasable_plans, recurrency, user_subscription, plans_hierarchy):
        full_html = []
        if purchasable_plans:
            for plan in purchasable_plans:
                if plan["plan_available_monthly"] and recurrency == "monthly" or plan["plan_available_annually"] and recurrency == "annually":
                    html = ReadWrite().read_html("checkout_upgrade_your_plan/_codes/html_plans_thumbs")
                    html.esc("plan_name_val", plan["plan_name_" + self.lang])
                    if self.user.user_cart_currency == "brl":
                        html.esc("plan_currency_val", StrFormat().format_currency_to_symbol("brl"))
                        if recurrency == "monthly":
                            html.esc("plan_price_actual_val", StrFormat().format_to_brl_money(plan["plan_price_monthly_brl_actual"], big=True))
                        if recurrency == "annually":
                            html.esc("plan_price_actual_val", StrFormat().format_to_brl_money(plan["plan_price_annually_brl_actual"], big=True))

                    elif self.user.user_cart_currency == "usd":
                        html.esc("plan_currency_val", StrFormat().format_currency_to_symbol("usd"))
                        if recurrency == "monthly":
                            html.esc("plan_price_actual_val", StrFormat().format_to_usd_money(plan["plan_price_monthly_usd_actual"], big=True))
                        if recurrency == "annually":
                            html.esc("plan_price_actual_val", StrFormat().format_to_usd_money(plan["plan_price_annually_usd_actual"], big=True))

                    if recurrency == "monthly":
                        html.esc("plan_recurrency_val", self.translate("mês"))
                        html.esc("plan_recurrency_phrase_val", self.translate("Cobrado mensalmente"))

                        if not plan["plan_available_annually"]:
                            html.esc("save_on_annually_visibility_val", "display:none;")
                        else:
                            if self.user.user_cart_currency == "brl":
                                html.esc("plan_annually_savings", 100 - int(int(plan["plan_price_annually_brl_actual"]) / (int(plan["plan_price_monthly_brl_actual"]) * 12) * 100))
                            elif self.user.user_cart_currency == "usd":
                                html.esc("plan_annually_savings", 100 - int(int(plan["plan_price_annually_usd_actual"]) / (int(plan["plan_price_monthly_usd_actual"]) * 12) * 100))

                    if recurrency == "annually":
                        html.esc("plan_recurrency_val", self.translate("ano"))
                        html.esc("save_on_annually_visibility_val", "display:none;")
                        html.esc("plan_recurrency_val", self.translate("ano"))
                        html.esc("plan_recurrency_phrase_val", self.translate("Cobrado anualmente"))

                    if user_subscription and (user_subscription.get("subscription_plan_id") == plan["plan_id"]) and (user_subscription.get("subscription_recurrency") == recurrency):
                        html.esc("html_your_plan_button_or_upgrade_plan_button", self.show_html_your_plan_button())
                    elif user_subscription and (user_subscription.get("subscription_plan_id") + "-" + user_subscription.get("subscription_recurrency") in plans_hierarchy) and (int(plans_hierarchy[user_subscription.get("subscription_plan_id") + "-" + user_subscription.get("subscription_recurrency")]) > int(plans_hierarchy[plan["plan_id"] + "-" + recurrency])):
                        html.esc("html_your_plan_button_or_upgrade_plan_button", self.show_html_upgrade_plan_button(plan["plan_id"], recurrency, "downgrade"))
                    else:
                        html.esc("html_your_plan_button_or_upgrade_plan_button", self.show_html_upgrade_plan_button(plan["plan_id"], recurrency, "upgrade"))

                    if plan["plan_has_trial"]:
                        trial_plan_version = Dynamo().get_plan(plan["plan_id"] + "-trial")
                        if trial_plan_version and plan["plan_id"] + "-trial" not in self.user.user_used_trials:
                            html.esc("html_trial_button", self.show_html_trial_button(plan, recurrency))

                    html.esc("plan_maxium_model_size_in_mbs_val", plan["plan_maxium_model_size_in_mbs"])
                    html.esc("plan_cloud_space_in_gbs_val", int(int(plan["plan_cloud_space_in_mbs"]) / 1000))
                    if not plan["plan_share_files"]:
                        html.esc("plan_share_files_visibility_val", "display:none;")
                    else:
                        html.esc("not_plan_share_files_visibility_val", "display:none;")

                    html.esc("plan_reference_tracker_val", self.translate(translate_reference_tracker(plan["plan_reference_tracker"])))
                    html.esc("plan_maxium_federated_size_in_mbs_val", plan["plan_maxium_federated_size_in_mbs"])
                    html.esc("plan_maxium_devices_available_val", plan["plan_maxium_devices_available"])
                    if not plan["plan_download_files"]:
                        html.esc("plan_download_files_visibility_val", "display:none;")
                    else:
                        html.esc("not_plan_download_files_visibility_val", "display:none;")

                    if plan["plan_team_play_participants"] == "0":
                        html.esc("plan_team_play_participants_visibility_val", "display:none;")
                    else:
                        html.esc("plan_team_play_participants_val", plan["plan_team_play_participants"])
                        html.esc("not_plan_team_play_participants_visibility_val", "display:none;")

                    full_html.append(str(html))
        return "".join(full_html)

    def show_html_your_plan_button(self):
        html = ReadWrite().read_html("checkout_upgrade_your_plan/_codes/html_your_plan_button")
        return str(html)

    def show_html_upgrade_plan_button(self, plan_id, recurrency, change):
        html = ReadWrite().read_html("checkout_upgrade_your_plan/_codes/html_upgrade_plan_button")
        html.esc("plan_id_val", plan_id)
        html.esc("recurrency_val", recurrency)
        if change == "downgrade":
            html.esc("upgrade_or_downgrade_val", self.translate("Downgrade de plano"))
        else:
            html.esc("upgrade_or_downgrade_val", self.translate("Upgrade de plano"))
        return str(html)

    def show_html_trial_button(self, plan, recurrency):
        html = ReadWrite().read_html("checkout_upgrade_your_plan/_codes/html_trial_button")
        html.esc("plan_id_val", plan["plan_id"])
        html.esc("plan_trial_duration_in_days_val", plan["plan_trial_duration_in_days"])
        html.esc("recurrency_val", recurrency)
        return str(html)
