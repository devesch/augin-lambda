from python_web_frame.panel_page import PanelPage
from objects.Order import generate_order_short_id, translate_order_payment_method, translate_order_type, translate_order_status
from utils.utils.Http import Http
from utils.utils.Date import Date
from utils.utils.ReadWrite import ReadWrite
from utils.utils.StrFormat import StrFormat
from utils.AWS.Dynamo import Dynamo


class PanelOrder(PanelPage):
    name = "Painel - Ordem"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        if not self.path.get("order"):
            return Http().redirect("panel_explore_project")
        if (self.path["order"]["order_user_id"] != self.user.user_id) and (self.user.user_credential != "admin"):
            return Http().redirect("panel_explore_project")

        html = super().parse_html()
        html.esc("user_name_val", self.user.user_name)
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

        order_plan = Dynamo().get_plan(self.path["order"]["order_plan_id"])
        html.esc("html_table_rows", self.list_html_table_rows(self.path["order"], order_plan))
        if self.path["order"]["order_user_cart_cupom"]:
            html.esc("html_order_cupom", self.show_html_order_cupom())
        if self.path["order"]["order_status"] == "paid":
            html.esc("html_print_payment_button", self.show_html_print_payment_button())
            if self.path["order"]["order_nfse_xml_link"]:
                if self.path["order"]["order_currency"] == "brl":
                    html.esc("html_download_xml_invoice_button", self.show_html_download_xml_invoice_button(self.path["order"]["order_nfse_xml_link"]))
            if self.path["order"]["order_nfse_pdf_link"]:
                html.esc("html_download_pdf_invoice_button", self.show_html_download_pdf_invoice_button(self.path["order"]["order_nfse_pdf_link"]))
            if not self.path["order"]["order_nfse_xml_link"] and not self.path["order"]["order_nfse_pdf_link"]:
                html.esc("nfse_visibilty_val", "display:none;")
        if self.path["order"]["order_status"] != "paid":
            html.esc("nfse_visibilty_val", "display:none;")
        return str(html)

    def render_post(self):
        return self.render_get()

    def show_html_print_payment_button(self):
        html = ReadWrite().read_html("panel_order/_codes/html_print_payment_button")
        return str(html)

    def show_html_download_xml_invoice_button(self, order_nfse_xml_link):
        html = ReadWrite().read_html("panel_order/_codes/html_download_xml_invoice_button")
        html.esc("order_nfse_xml_link_val", order_nfse_xml_link)
        return str(html)

    def show_html_download_pdf_invoice_button(self, order_nfse_pdf_link):
        html = ReadWrite().read_html("panel_order/_codes/html_download_pdf_invoice_button")
        html.esc("order_nfse_pdf_link_val", order_nfse_pdf_link)
        return str(html)

    def show_html_order_cupom(self):
        html = ReadWrite().read_html("panel_order/_codes/html_order_cupom")
        html.esc("order_currency_val", ReadWrite().convert_currency_to_symbol(self.path["order"]["order_currency"]))
        if self.path["order"]["order_user_cart_cupom"]["cupom_type"] == "percentage_discount" or self.path["order"]["order_user_cart_cupom"]["cupom_type"] == "total_discount":
            if self.path["order"]["order_currency"] == "brl":
                html.esc("order_sub_total_brl_price_val", ReadWrite().format_to_money(self.path["order"]["order_sub_total_brl_price"], "brl"))
                html.esc("order_cupom_feature_val", "- " + ReadWrite().convert_currency_to_symbol(self.path["order"]["order_currency"]) + " " + ReadWrite().format_to_money(self.path["order"]["order_brl_discount"], "brl"))
            elif self.path["order"]["order_currency"] == "usd":
                html.esc("order_sub_total_usd_price_val", ReadWrite().format_to_money(self.path["order"]["order_sub_total_usd_price"], "usd"))
                html.esc("order_cupom_feature_val", "- " + StrFormat().format_currency_to_symbol(self.path["order"]["order_currency"]) + " " + ReadWrite().format_to_money(self.path["order"]["order_usd_discount"], "usd"))
            elif self.user.user_cart_cupom["cupom_type"] == "free_product":
                html.esc("order_cupom_feature_val", self.path["order"]["order_user_cart_cupom"]["cupom_product_address"])
        return str(html)

    def list_html_table_rows(self, order, order_plan):
        # full_html = []
        # for product_address, product in order_updated_cart.items():
        html = ReadWrite().read_html("panel_order/_codes/html_table_rows")
        html.esc("product_name_val", order_plan["plan_name_" + self.lang])
        # html.esc("product_quantity_val", "1")
        html.esc("product_currency_val", StrFormat().format_currency_to_symbol(order["order_currency"]))
        html.esc("product_total_price", StrFormat().format_to_money(order["order_sub_total_" + order["order_currency"] + "_price"], order["order_currency"]))
        return str(html)
        #     if self.check_if_product_is_available(product_address, product["product_recurrency"]):
        #         if self.check_if_product_is_unique(product):
        #             html.esc("html_buy_again", self.show_html_buy_again(product_address))
        #     full_html.append(str(html))
        # return "".join(full_html)

    def check_if_product_is_unique(self, product_recurrency):
        if product_recurrency == "unique":
            return True
        return False

    # def show_html_buy_again(self, product_address):
    #     html = ReadWrite().read_html("panel_order/_codes/html_buy_again")
    #     html.esc("product_address_val", product_address)
    #     html.esc("user_auth_token_val", self.user.user_auth_token)
    #     return str(html)

    def check_if_product_is_available(self, product_address, product):
        product = self.dynamo.get_product(product_address)
        if product:
            if not product["product_is_promo"]:
                if product["product_available"]:
                    return True
        return False
