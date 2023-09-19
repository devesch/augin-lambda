from python_web_frame.panel_page import PanelPage
from utils.Config import lambda_constants
from objects.Plan import translate_reference_tracker
from objects.Order import translate_order_status
from utils.utils.ReadWrite import ReadWrite
from utils.utils.StrFormat import StrFormat
from utils.utils.Date import Date
from utils.AWS.Dynamo import Dynamo


class PanelYourPlan(PanelPage):
    name = "Painel - Seu Plano"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        user_subscription = None
        if self.user.user_subscription_id:
            user_subscription = Dynamo().get_subscription(self.user.user_subscription_id)

        user_plan = self.user.get_user_actual_plan()

        html = super().parse_html()
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
            html.esc("plan_team_play_val", self.translate("Sim"))
        else:
            html.esc("plan_team_play_val", self.translate("Não"))

        if not user_subscription:
            html.esc("user_subscription_currency_val", StrFormat().format_currency_to_symbol(self.user.user_cart_currency))
            html.esc("user_subscription_price_val", "-")
            html.esc("user_subscription_recurrency_val", "-")
            html.esc("user_subscription_valid_until_val", "-")
        else:
            html.esc("user_subscription_currency_val", StrFormat().format_currency_to_symbol(user_subscription["subscription_currency"]))
            html.esc("user_subscription_price_val", StrFormat().format_to_money(user_subscription["subscription_price"], user_subscription["subscription_currency"]))
            html.esc("user_subscription_recurrency_val", StrFormat().format_recurrency(user_subscription["subscription_recurrency"]).title())
            html.esc("user_subscription_valid_until_val", Date().format_to_str_time(user_subscription["subscription_valid_until"]))
            subscription_payment_method = Dynamo().get_payment_method(self.user.user_id, user_subscription["subscription_default_payment_method"])
            html.esc("user_subscription_payment_method_val", StrFormat().format_to_payment_method(subscription_payment_method["payment_method_type"]))

        if not self.user.user_plan_id:
            html.esc("html_upgrade_plan_button", str(ReadWrite().read_html("panel_your_plan/_codes/html_upgrade_plan_button")))

        user_orders = Dynamo().query_user_orders(self.user.user_id)
        if user_orders:
            html.esc("html_payment_history_div", self.show_html_payment_history_div(user_orders))
        user_payment_methods = Dynamo().query_user_payment_methods(self.user.user_id)
        if user_payment_methods:
            html.esc("html_payment_methods_div", self.show_html_payment_methods_div(user_payment_methods))
        return str(html)

    def render_post(self):
        return self.render_get()

    def show_html_payment_history_div(self, user_orders):
        html = ReadWrite().read_html("panel_your_plan/_codes/html_payment_history_div")
        html.esc("html_payment_history_rows", self.list_html_payment_history_rows(user_orders))
        return str(html)

    def list_html_payment_history_rows(self, user_orders):
        plan_id_name_conversion = {}
        full_html = []
        for order in user_orders:
            html = ReadWrite().read_html("panel_your_plan/_codes/html_payment_history_rows")
            html.esc("order_created_at_val", Date().format_to_str_time(order["created_at"]))
            html.esc("order_currency_symbol_val", StrFormat().format_currency_to_symbol(order["order_currency"]))
            html.esc("order_price_val", StrFormat().format_to_money(order["order_total_price"], order["order_currency"]))
            html.esc("order_status_val", translate_order_status(order["order_status"]))

            if order["order_status"] == "paid":
                html.esc("order_status_class_val", "paid")
            else:
                html.esc("order_status_class_val", "failed")

            if order["order_plan_id"] not in plan_id_name_conversion:
                plan_id_name_conversion[order["order_plan_id"]] = Dynamo().get_plan(order["order_plan_id"])
            html.esc("order_plan_name_val", plan_id_name_conversion[order["order_plan_id"]]["plan_name_" + self.lang])

            full_html.append(str(html))
        return "".join(full_html)

    def show_html_payment_methods_div(self, user_payment_methods):
        html = ReadWrite().read_html("panel_your_plan/_codes/html_payment_methods_div")
        html.esc("html_payment_methods_rows", self.list_html_payment_methods_rows(user_payment_methods))
        return str(html)

    def list_html_payment_methods_rows(self, user_payment_methods):
        full_html = []
        for payment_method in user_payment_methods:
            if payment_method["payment_method_type"] == "card":
                html = ReadWrite().read_html("panel_your_plan/_codes/html_payment_methods_rows")
                html.esc("brand_val", payment_method["payment_method_card"]["brand"])
                html.esc("title_brand_val", payment_method["payment_method_card"]["brand"].title())
                html.esc("last4_val", payment_method["payment_method_card"]["last4"])
                html.esc("exp_month_val", payment_method["payment_method_card"]["exp_month"])
                html.esc("exp_year_val", payment_method["payment_method_card"]["exp_year"])
                full_html.append(str(html))
        return "".join(full_html)
