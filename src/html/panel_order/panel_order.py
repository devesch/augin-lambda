from objects.Order import generate_order_short_id, translate_order_payment_method, translate_order_type, translate_order_status
from python_web_frame.panel_page import PanelPage
from utils.utils.StrFormat import StrFormat
from utils.utils.ReadWrite import ReadWrite
from utils.utils.JsonData import JsonData
from utils.AWS.Dynamo import Dynamo
from objects.User import load_user
from utils.utils.Http import Http
from utils.utils.Date import Date


class PanelOrder(PanelPage):
    name = "Painel - Ordem"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        if not self.path.get("order"):
            return Http().redirect("panel_explore_project")
        if self.path.get("not_render_menu"):
            self.user = load_user(self.path["order"]["order_user_id"])
        if (self.path["order"]["order_user_id"] != self.user.user_id) and (self.user.user_credential != "admin"):
            return Http().redirect("panel_explore_project")

        html = super().parse_html()
        if self.path.get("not_render_menu"):
            html.esc("download_print_page_buttons_visibility_val", "display:none;")
        if not self.path or not self.path.get("not_render_menu"):
            html.esc("my_plan_main_class_val", "my-plan__main")

        html.esc("order_id_val", self.path["order"]["order_id"])
        html.esc("user_name_val", self.user.user_name)
        html.esc("user_email_val", self.user.user_email)
        html.esc("user_country_code_val", JsonData().get_country_phone_code()[self.user.user_address_data["user_country"]])
        if self.user.user_address_data["user_country"] == "BR":
            html.esc("user_phone_val", StrFormat().format_to_phone(self.user.user_phone))
        html.esc("user_phone_val", self.user.user_phone)

        html.esc("order_short_id_val", generate_order_short_id(self.path["order"]["order_id"]))
        html.esc("order_id_val", self.path["order"]["order_id"])
        html.esc("order_payment_method", translate_order_payment_method(self.path["order"]["order_payment_method"]))
        if self.path["order"]["order_currency"] == "brl":
            html.esc("order_datetime_val", Date().format_unixtime_to_br_datetime(self.path["order"]["created_at"]))
        elif self.path["order"]["order_currency"] == "usd":
            html.esc("order_datetime_val", Date().format_unixtime_to_inter_datetime(self.path["order"]["created_at"]))
        html.esc("order_type_val", translate_order_type(self.path["order"]["order_type"]))
        html.esc("order_status_val", translate_order_status(self.path["order"]["order_status"]))
        html.esc("order_currency_val", StrFormat().format_currency_to_symbol(self.path["order"]["order_currency"]))
        html.esc("order_total_price_val", StrFormat().format_to_money(self.path["order"]["order_total_price"], self.path["order"]["order_currency"]))
        html.esc("order_sub_total_price_val", StrFormat().format_to_money(self.path["order"]["order_sub_total_" + self.path["order"]["order_currency"] + "_price"], self.path["order"]["order_currency"]))
        html.esc("order_discount_price_val", StrFormat().format_to_money(self.path["order"]["order_" + self.path["order"]["order_currency"] + "_discount"], self.path["order"]["order_currency"]))
        html.esc("order_total_price_val", StrFormat().format_to_money(self.path["order"]["order_total_price"], self.path["order"]["order_currency"]))

        order_plan = Dynamo().get_plan(self.path["order"]["order_plan_id"])
        html.esc("html_order_table_rows", self.list_html_order_table_rows(self.path["order"], order_plan))

        if self.path["order"]["order_nfse_status"] != "issued":
            html.esc("nfse_visibilty_val", "display:none;")
        else:
            html.esc("order_nfse_number_val", self.path["order"]["order_nfse_number"])
            html.esc("order_nfse_created_at_val", Date().format_unixtime_to_br_datetime(self.path["order"]["order_nfse_created_at"]))
            html.esc("order_nfse_pdf_link_val", self.path["order"]["order_nfse_pdf_link"])
            html.esc("order_nfse_xml_link_val", self.path["order"]["order_nfse_xml_link"])

        if not self.path["order"]["order_payment_stripe_receipt_url"]:
            html.esc("order_payment_stripe_receipt_url_visibility_val", "display:none;")
        else:
            html.esc("order_payment_stripe_receipt_url_val", self.path["order"]["order_payment_stripe_receipt_url"])
            html.esc("order_payment_service_id_val", self.path["order"]["order_payment_service_id"])
            if self.path["order"]["order_currency"] == "brl" and self.path["order"].get("order_paid_at"):
                html.esc("order_paid_at_val", Date().format_unixtime_to_br_datetime(self.path["order"]["order_paid_at"]))
            elif self.path["order"]["order_currency"] == "usd" and self.path["order"].get("order_paid_at"):
                html.esc("order_paid_at_val", Date().format_unixtime_to_inter_datetime(self.path["order"]["order_paid_at"]))

        if not self.path["order"]["order_payment_stripe_boleto_url"]:
            html.esc("order_payment_stripe_boleto_visibility_val", "display:none;")
        else:
            html.esc("order_payment_stripe_boleto_url_val", self.path["order"]["order_payment_stripe_boleto_url"])

        return str(html)

    def render_post(self):
        return self.render_get()

    def show_html_order_coupon(self):
        html = ReadWrite().read_html("panel_order/_codes/html_order_coupon")
        html.esc("order_currency_val", StrFormat().format_currency_to_symbol(self.path["order"]["order_currency"]))
        if self.path["order"]["order_currency"] == "brl":
            html.esc("order_sub_total_brl_price_val", StrFormat().format_to_money(self.path["order"]["order_sub_total_brl_price"], "brl"))
            html.esc("order_coupon_feature_val", "- " + StrFormat().format_currency_to_symbol(self.path["order"]["order_currency"]) + " " + StrFormat().format_to_money(self.path["order"]["order_brl_discount"], "brl"))
        elif self.path["order"]["order_currency"] == "usd":
            html.esc("order_sub_total_usd_price_val", StrFormat().format_to_money(self.path["order"]["order_sub_total_usd_price"], "usd"))
            html.esc("order_coupon_feature_val", "- " + StrFormat().format_currency_to_symbol(self.path["order"]["order_currency"]) + " " + StrFormat().format_to_money(self.path["order"]["order_usd_discount"], "usd"))
        return str(html)

    def list_html_order_table_rows(self, order, order_plan):
        # full_html = []
        # for product_address, product in order_updated_cart.items():
        html = ReadWrite().read_html("panel_order/_codes/html_order_table_rows")
        html.esc("product_name_val", order_plan["plan_name_" + self.lang])
        html.esc("product_quantity_val", "1")
        html.esc("product_currency_val", StrFormat().format_currency_to_symbol(order["order_currency"]))
        html.esc("product_total_price", StrFormat().format_to_money(order["order_sub_total_" + order["order_currency"] + "_price"], order["order_currency"]))
        html.esc("product_starting_date_val", Date().format_to_str_time(order["created_at"], without_year=True))
        if order["order_plan_recurrency"] == "annually":
            html.esc("product_until_date_val", Date().format_to_str_time(float(order["created_at"]) + 2628000))
        if order["order_plan_recurrency"] == "monthly":
            html.esc("product_until_date_val", Date().format_to_str_time(float(order["created_at"]) + 31536000))
        return str(html)

    def check_if_product_is_unique(self, product_recurrency):
        return product_recurrency == "unique"

    def check_if_product_is_available(self, product_address, product):
        product = self.dynamo.get_product(product_address)
        if product:
            if not product["product_is_promo"]:
                if product["product_available"]:
                    return True
        return False
