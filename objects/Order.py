from time import time
from utils.utils.StrFormat import StrFormat


class Order:
    def __init__(self, user_id, order_id) -> None:
        self.pk = "user#" + user_id
        self.sk = "order#" + order_id
        self.order_user_id = user_id
        self.order_id = order_id
        self.order_plan_id = ""
        self.order_plan_recurrency = ""
        self.order_status = "not_active"
        self.order_descrimination = ""
        self.order_nfse_id = ""
        self.order_nfse_status = "not_issued"  # "not_issued" / "issued" / "canceled"
        self.order_nfse_number = ""
        self.order_nfse_serie = ""
        self.order_nfse_type = ""
        self.order_nfse_xml_link = ""
        self.order_nfse_pdf_link = ""
        self.order_nfse_canceled_at = ""
        self.order_nfse_created_at = ""
        self.order_type = ""
        self.order_payment_method = ""
        self.order_sub_total_brl_price = ""
        self.order_sub_total_usd_price = ""
        self.order_brl_discount = ""
        self.order_usd_discount = ""
        self.order_brl_price = ""
        self.order_usd_price = ""
        self.order_total_price = ""
        self.order_currency = ""
        self.order_installment_quantity = ""
        self.order_payment_service = ""
        self.order_payment_service_id = ""
        self.order_payment_stripe_subscription_id = ""
        self.order_payment_stripe_charge_id = ""
        self.order_user_cart_cupom = {}
        self.created_at = str(time())
        self.entity = "order"


def generate_order_descrimination(product_name, product_brl_price):
    order_descrimination = []
    total_price = StrFormat().format_to_brl_money(product_brl_price)
    order_descrimination.append(f"1x {product_name}: R${total_price}")

    order_descrimination_str = " | ".join(order_descrimination)
    tribute_value = StrFormat().format_to_brl_money(int(int(product_brl_price) * 0.1797))
    order_descrimination_str += f"\n CONFORME LEI 12.741/2012 o valor aproximado dos tributos é R$ {tribute_value} (17,97%), FONTE: IBPT/empresometro.com.br (21.1.F)"

    return order_descrimination_str


def generate_order_short_id(order_id):
    return order_id[-6:]
