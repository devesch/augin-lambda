from python_web_frame.controllers.stripe_controller import StripeController
from objects.BackofficeData import increase_backoffice_data_total_count
from objects.Plan import generate_plan_price_with_coupon_discount
from utils.utils.StrFormat import StrFormat
from utils.AWS.Dynamo import Dynamo
from utils.Code import Code
from time import time


class Order:
    def __init__(self, user_id, order_id) -> None:
        self.pk = "user#" + user_id
        self.sk = "order#" + str(time())
        self.order_user_id = user_id
        self.order_id = order_id
        self.order_plan_id = ""
        self.order_plan_recurrency = ""
        self.order_status = "not_active"
        self.order_descrimination = ""
        self.order_last_error_code = ""
        self.order_last_error_message = ""
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
        self.order_payment_stripe_receipt_url = ""
        self.order_payment_stripe_boleto_url = ""
        self.order_user_cart_coupon_code = ""
        self.created_at = str(time())
        self.entity = "order"


def generate_order_descrimination(product_name, product_brl_price):
    order_descrimination = []
    total_price = StrFormat().format_to_brl_money(product_brl_price)
    order_descrimination.append(f"1x {product_name}: R${total_price}")

    order_descrimination_str = " | ".join(order_descrimination)
    tribute_value = StrFormat().format_to_brl_money(int(int(product_brl_price) * 0.1545))
    order_descrimination_str += f"\n CONFORME LEI 12.741/2012 o valor aproximado dos tributos é R$ {tribute_value} (15,45%), FONTE: IBPT/empresometro.com.br (21.1.F)"

    return order_descrimination_str


def generate_order_short_id(order_id):
    return order_id[-6:]


def translate_order_payment_method(order_payment_method):
    if order_payment_method == "card":
        return Code().translate("Cartão de crédito")
    if order_payment_method == "boleto":
        return Code().translate("Boleto")
    if order_payment_method == "pix":
        return Code().translate("Pix")
    if order_payment_method == "direct":
        return Code().translate("Pagamento Direto")
    if order_payment_method == "free_checkout":
        return Code().translate("Creditado pela Augin")


def translate_order_type(order_type):
    if order_type == "unique":
        return Code().translate("Compra única")
    elif order_type == "monthly" or order_type == "annually":
        return Code().translate("Assinatura")


def translate_order_status(order_status):
    translations = {"pending": "Incompleto", "paid": "Pago", "not_authorized": "Não autorizado", "card_declined": "Cartão negado", "expired_card": "Cartão expirado", "blocked_card": "Cartão bloqueado", "canceled_card": "Cartão cancelado", "problems_with_card": "Problemas no cartão", "time_out": "Excedeu o limite de tentativas", "refunded": "Reembolsado", "waiting_payment": "Aguardando pagamento", "error": "Erro"}

    translated_status = translations.get(order_status)
    if translated_status:
        return Code().translate(translated_status)
    else:
        return order_status


def check_if_order_is_in_refund_time(order_created_at):
    import time

    return float(order_created_at) + 604800 > time.time()


def translate_order_nfse_status(order_nfse_status):
    if order_nfse_status == "not_issued":
        return Code().translate("Não Emitida")
    elif order_nfse_status == "issued":
        return Code().translate("Emitida")
    elif order_nfse_status == "canceled":
        return Code().translate("Cancelada")


def remove_pendings_from_orders(orders):
    filtered_orders = []
    first_incompleted = False
    if orders:
        for order in orders:
            if order["order_status"] != "pending":
                filtered_orders.append(order)
            elif not first_incompleted:
                filtered_orders.append(order)
                first_incompleted = True
    return filtered_orders


def create_order_with_stripe_request_subscription(user, plan, plan_recurrency, stripe_request_payload):
    new_order = Order(user.user_id, stripe_request_payload["latest_invoice"]["payment_intent"].stripe_id)
    new_order.order_status = StripeController().convert_stripe_status_code_to_status(stripe_request_payload["status"])
    new_order.order_type = StripeController().convert_stripe_plan_interval_to_recurrence(stripe_request_payload["plan"]["interval"])

    if user.user_cart_coupon_code:
        if plan_recurrency == "annually":
            new_order.order_sub_total_brl_price = plan["plan_price_annually_brl"]
            new_order.order_sub_total_usd_price = plan["plan_price_annually_usd"]

            order_brl_price, order_brl_discount = generate_plan_price_with_coupon_discount(plan, user.user_cart_coupon_code, "annually", "brl")
            order_usd_price, order_usd_discount = generate_plan_price_with_coupon_discount(plan, user.user_cart_coupon_code, "annually", "usd")
            new_order.order_brl_discount = order_brl_discount
            new_order.order_usd_discount = order_usd_discount
            new_order.order_brl_price = order_brl_price
            new_order.order_usd_price = order_usd_price

        if plan_recurrency == "monthly":
            new_order.order_sub_total_brl_price = plan["plan_price_monthly_brl_actual"]
            new_order.order_sub_total_usd_price = plan["plan_price_monthly_usd_actual"]

            order_brl_price, order_brl_discount = generate_plan_price_with_coupon_discount(plan, user.user_cart_coupon_code, "monthly", "brl")
            order_usd_price, order_usd_discount = generate_plan_price_with_coupon_discount(plan, user.user_cart_coupon_code, "monthly", "usd")
            new_order.order_brl_discount = order_brl_discount
            new_order.order_usd_discount = order_usd_discount
            new_order.order_brl_price = order_brl_price
            new_order.order_usd_price = order_usd_price

    else:
        if plan_recurrency == "annually":
            new_order.order_sub_total_brl_price = plan["plan_price_annually_brl_actual"]
            new_order.order_sub_total_usd_price = plan["plan_price_annually_usd_actual"]
            new_order.order_brl_price = plan["plan_price_annually_brl_actual"]
            new_order.order_usd_price = plan["plan_price_annually_usd_actual"]

        if plan_recurrency == "monthly":
            new_order.order_sub_total_brl_price = plan["plan_price_monthly_brl_actual"]
            new_order.order_sub_total_usd_price = plan["plan_price_monthly_usd_actual"]
            new_order.order_brl_price = plan["plan_price_monthly_brl_actual"]
            new_order.order_usd_price = plan["plan_price_monthly_usd_actual"]

    new_order.order_total_price = stripe_request_payload["plan"]["amount_decimal"]
    new_order.order_currency = stripe_request_payload["plan"]["currency"]
    new_order.order_installment_quantity = "0001"
    new_order.order_payment_service = "stripe"
    new_order.order_payment_service_id = stripe_request_payload["latest_invoice"]["payment_intent"].stripe_id
    new_order.order_payment_stripe_subscription_id = stripe_request_payload.stripe_id
    new_order.order_plan_id = plan["plan_id"]
    new_order.order_plan_recurrency = plan_recurrency
    new_order.order_user_cart_coupon_code = user.user_cart_coupon_code
    new_order.order_descrimination = generate_order_descrimination(plan["plan_name_pt"], new_order.order_brl_price)
    Dynamo().put_entity(new_order.__dict__)
    increase_backoffice_data_total_count("order")


def create_order_with_stripe_subscription_updated(user, plan, plan_recurrency, stripe_subscription, payment_intent, invoice):
    new_order = Order(user.user_id, payment_intent["id"])
    new_order.order_status = StripeController().convert_stripe_status_code_to_status(payment_intent["status"])
    new_order.order_type = StripeController().convert_stripe_plan_interval_to_recurrence(stripe_subscription["plan"]["interval"])

    if stripe_subscription["metadata"].get("coupon_code"):
        if plan_recurrency == "annually":
            new_order.order_sub_total_brl_price = plan["plan_price_annually_brl"]
            new_order.order_sub_total_usd_price = plan["plan_price_annually_usd"]

            order_brl_price, order_brl_discount = generate_plan_price_with_coupon_discount(plan, stripe_subscription["metadata"]["coupon_code"], "annually", "brl")
            order_usd_price, order_usd_discount = generate_plan_price_with_coupon_discount(plan, stripe_subscription["metadata"]["coupon_code"], "annually", "usd")
            new_order.order_brl_discount = order_brl_discount
            new_order.order_usd_discount = order_usd_discount
            new_order.order_brl_price = order_brl_price
            new_order.order_usd_price = order_usd_price

        if plan_recurrency == "monthly":
            new_order.order_sub_total_brl_price = plan["plan_price_monthly_brl_actual"]
            new_order.order_sub_total_usd_price = plan["plan_price_monthly_usd_actual"]

            order_brl_price, order_brl_discount = generate_plan_price_with_coupon_discount(plan, "monthly", "brl")
            order_usd_price, order_usd_discount = generate_plan_price_with_coupon_discount(plan, "monthly", "usd")
            new_order.order_brl_discount = order_brl_discount
            new_order.order_usd_discount = order_usd_discount
            new_order.order_brl_price = order_brl_price
            new_order.order_usd_price = order_usd_price

    else:
        if plan_recurrency == "annually":
            new_order.order_sub_total_brl_price = plan["plan_price_annually_brl_actual"]
            new_order.order_sub_total_usd_price = plan["plan_price_annually_usd_actual"]
            new_order.order_brl_price = plan["plan_price_annually_brl_actual"]
            new_order.order_usd_price = plan["plan_price_annually_usd_actual"]

        if plan_recurrency == "monthly":
            new_order.order_sub_total_brl_price = plan["plan_price_monthly_brl_actual"]
            new_order.order_sub_total_usd_price = plan["plan_price_monthly_usd_actual"]
            new_order.order_brl_price = plan["plan_price_monthly_brl_actual"]
            new_order.order_usd_price = plan["plan_price_monthly_usd_actual"]

    new_order.order_total_price = str(payment_intent["amount"])
    new_order.order_currency = payment_intent["currency"]
    new_order.order_installment_quantity = invoice["number"][9:]
    new_order.order_payment_service = "stripe"
    new_order.order_payment_service_id = payment_intent["id"]
    new_order.order_payment_stripe_subscription_id = stripe_subscription.stripe_id
    new_order.order_plan_id = plan["plan_id"]
    new_order.order_plan_recurrency = plan_recurrency
    new_order.order_user_cart_coupon_code = stripe_subscription["metadata"].get("coupon_code", "")
    new_order.order_descrimination = generate_order_descrimination(plan["plan_name_pt"], new_order.order_brl_price)
    Dynamo().put_entity(new_order.__dict__)
    increase_backoffice_data_total_count("order")
