from python_web_frame.panel_page import PanelPage
from python_web_frame.controllers.stripe_controller import stripe_token
from objects.Plan import translate_reference_tracker
from objects.Order import remove_pendings_from_orders
from utils.utils.ReadWrite import ReadWrite
from utils.utils.StrFormat import StrFormat
from utils.utils.Date import Date
from utils.utils.Sort import Sort
from utils.AWS.Dynamo import Dynamo


class PanelYourPlan(PanelPage):
    name = "Painel - Seu Plano"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        user_subscription = None
        user_plan = self.user.get_user_actual_plan()
        if self.user.user_subscription_id:
            user_subscription = Dynamo().get_subscription(self.user.user_subscription_id)

        html = super().parse_html()
        html.esc("html_upgrade_button", self.show_html_upgrade_button(user_plan))
        html.esc("html_notifications_button", self.show_html_notifications_button())
        html.esc("user_name_val", self.user.user_name.title())
        html.esc("plan_name_val", user_plan["plan_name_" + self.lang])
        html.esc("plan_maxium_model_size_in_mbs_val", user_plan["plan_maxium_model_size_in_mbs"])
        html.esc("plan_cloud_space_in_gbs_val", int(int(user_plan["plan_cloud_space_in_mbs"]) / 1000))
        if user_plan["plan_share_files"]:
            html.esc("plan_share_files_val", self.translate("Sim"))
        else:
            html.esc("plan_share_files_val", self.translate("Não"))
        html.esc("plan_reference_tracker_val", self.translate(translate_reference_tracker(user_plan["plan_reference_tracker"])))
        if user_plan["plan_maxium_federated_size_in_mbs"] == "0":
            html.esc("plan_maxium_federated_size_in_mbs_val", self.translate("Não"))
        else:
            html.esc("plan_maxium_federated_size_in_mbs_val", user_plan["plan_maxium_federated_size_in_mbs"] + " Mb")
        html.esc("plan_maxium_devices_available_val", user_plan["plan_maxium_devices_available"])
        if user_plan["plan_download_files"]:
            html.esc("plan_download_files_val", self.translate("Sim"))
        else:
            html.esc("plan_download_files_val", self.translate("Não"))
        if int(user_plan["plan_team_play_participants"]) > 0:
            html.esc("plan_team_play_val", user_plan["plan_team_play_participants"])
        else:
            html.esc("plan_team_play_val", self.translate("Não"))

        if not user_subscription:
            html.esc("html_user_has_no_subscription", self.show_html_user_has_no_subscription(user_plan))
            html.esc("html_upgrade_plan_button", str(ReadWrite().read_html("panel_your_plan/_codes/html_upgrade_plan_button")))
        else:
            if user_subscription["subscription_is_trial"]:
                html.esc("html_user_subscription_is_trial", self.show_html_user_subscription_is_trial(user_subscription, user_plan))
                html.esc("html_upgrade_plan_button", str(ReadWrite().read_html("panel_your_plan/_codes/html_upgrade_plan_button")))
            else:
                html.esc("html_user_subscription", self.show_html_user_subscription(user_subscription, user_plan))
                if user_subscription["subscription_status"] == "active":
                    free_plan = Dynamo().get_free_plan()
                    html.esc("html_cancel_subscription_button", self.show_html_cancel_subscription_button())
                    html.esc("subscription_valid_until_val", Date().format_to_str_time(user_subscription["subscription_valid_until"]))
                    html.esc("free_plan_cloud_space_in_gbs_val", int(int(free_plan["plan_cloud_space_in_mbs"]) / 1000))
                    html.esc("free_plan_maxium_model_size_in_mbs_val", free_plan["plan_maxium_model_size_in_mbs"])
                else:
                    html.esc("html_upgrade_plan_button", str(ReadWrite().read_html("panel_your_plan/_codes/html_upgrade_plan_button")))

        user_orders = Dynamo().query_user_orders(self.user.user_id)
        user_orders = remove_pendings_from_orders(user_orders)
        if user_orders:
            html.esc("html_payment_history_div", self.show_html_payment_history_div(user_orders))
        user_payment_methods = Dynamo().query_user_payment_methods(self.user.user_id)
        if user_payment_methods:
            html.esc("html_payment_methods_div", self.show_html_payment_methods_div(user_payment_methods, user_subscription))

        html.esc("stripe_token_val", stripe_token)
        html.esc("lang_val", self.lang)
        html.esc("country_val", self.user.user_address_data["user_country"])
        return str(html)

    def render_post(self):
        return self.render_get()

    def show_html_cancel_subscription_button(self):
        html = ReadWrite().read_html("panel_your_plan/_codes/html_cancel_subscription_button")
        return str(html)

    def show_html_user_has_no_subscription(self, user_plan):
        html = ReadWrite().read_html("panel_your_plan/_codes/html_user_has_no_subscription")
        html.esc("plan_name_val", user_plan["plan_name_" + self.lang])
        html.esc("user_subscription_status_val", "-")
        html.esc("user_subscription_currency_val", StrFormat().format_currency_to_symbol(self.user.user_cart_currency))
        html.esc("user_subscription_price_val", StrFormat().format_to_money("0000", self.user.user_cart_currency))
        html.esc("user_subscription_valid_until_val", self.translate("Ilimitado"))
        return str(html)

    def show_html_user_subscription(self, user_subscription, user_plan):
        html = ReadWrite().read_html("panel_your_plan/_codes/html_user_subscription")
        html.esc("plan_name_val", user_plan["plan_name_" + self.lang])
        html.esc("user_subscription_currency_val", StrFormat().format_currency_to_symbol(user_subscription["subscription_currency"]))
        html.esc("user_subscription_status_val", self.translate(StrFormat().format_status(user_subscription["subscription_status"])))
        html.esc("user_subscription_price_val", StrFormat().format_to_money(user_subscription["subscription_price"], user_subscription["subscription_currency"]))
        html.esc("user_subscription_recurrency_val", StrFormat().format_recurrency(user_subscription["subscription_recurrency"]).title())
        html.esc("user_subscription_valid_until_val", Date().format_to_str_time(user_subscription["subscription_valid_until"]))
        if user_subscription["subscription_default_payment_method"]:
            subscription_payment_method = Dynamo().get_payment_method(self.user.user_id, user_subscription["subscription_default_payment_method"])
            html.esc("user_subscription_payment_method_val", StrFormat().format_to_payment_method(subscription_payment_method["payment_method_type"]))
        else:
            html.esc("user_subscription_payment_method_val", "-")

        if user_subscription["subscription_status"] == "active":
            html.esc("user_subscription_valid_until_visibility_val", "none")
        else:
            html.esc("user_subscription_active_visibility_val", "none")
        return str(html)

    def show_html_user_subscription_is_trial(self, user_subscription, user_plan):
        html = ReadWrite().read_html("panel_your_plan/_codes/html_user_subscription_is_trial")
        html.esc("plan_name_val", user_plan["plan_name_" + self.lang])
        html.esc("user_subscription_status_val", self.translate(StrFormat().format_status(user_subscription["subscription_status"])))
        html.esc("user_subscription_currency_val", StrFormat().format_currency_to_symbol(user_subscription["subscription_currency"]))
        html.esc("user_subscription_price_val", StrFormat().format_to_money(user_subscription["subscription_price"], user_subscription["subscription_currency"]))
        html.esc("user_subscription_valid_until_val", Date().format_to_str_time(user_subscription["subscription_valid_until"]))
        return str(html)
