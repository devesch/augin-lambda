from python_web_frame.backoffice_page import BackofficePage
from objects.Order import Order, check_if_order_is_in_refund_time
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Ses import Ses
from utils.utils.ReadWrite import ReadWrite
from python_web_frame.controllers.billing_controller import BillingController
from python_web_frame.controllers.stripe_controller import StripeController

import json


class BackofficeOrders(BackofficePage):
    name = "Backoffice - Pagamentos"
    public = False
    bypass = False
    admin = True

    def render_get(self):
        backoffice_data = self.get_backoffice_data()

        # if Validation().check_if_local_env():
        #     orders, last_evaluated_key = Dynamo().query_paginated_all_orders(limit=int(10000000))
        #     backoffice_data["backoffice_data_total_order_count"] = str(len(orders))
        #     Dynamo().put_entity(backoffice_data)

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)

        # if self.post.get("showing_total_count"):
        #     if self.path.get("order_status") and self.path.get("order_status") != "all":
        #         orders, last_evaluated_key = Dynamo().query_paginated_all_orders_from_status(self.path["order_status"], limit=int(self.post["showing_total_count"]))
        #     else:
        #         orders, last_evaluated_key = Dynamo().query_paginated_all_orders(limit=int(self.post["showing_total_count"]))
        # else:
        #     if self.path.get("order_status") and self.path.get("order_status") != "all":
        #         orders, last_evaluated_key = Dynamo().query_paginated_all_orders_from_status(self.path["order_status"], limit=int(self.user.user_pagination_count))
        #     else:
        #         orders, last_evaluated_key = Dynamo().query_paginated_all_orders(limit=int(self.user.user_pagination_count))

        # if self.path.get("order_status"):
        #     html.esc("pre_sel_" + self.path["order_status"] + "_val", 'selected="selected"')
        #     query = "query_paginated_all_orders_from_status"
        # else:
        #     query = "query_paginated_all_orders"

        orders, last_evaluated_key = Dynamo().query_paginated_all_orders(limit=int(self.user.user_pagination_count))
        query = "query_paginated_all_orders"

        html.esc("html_pagination", self.show_html_pagination(len(orders), backoffice_data["backoffice_data_total_order_count"], query, last_evaluated_key, self.path.get("order_status", "")))
        html.esc("last_evaluated_key_val", json.dumps(last_evaluated_key))
        html.esc("showing_total_count_val", len(orders))

        html.esc("html_backoffice_orders_table_rows", self.list_html_backoffice_orders_table_rows(orders))
        return str(html)

    def render_post(self):
        if self.post.get("command") == "re_issue_order_nfse":
            order = Dynamo().get_order(self.post["order_id"])
            if not order:
                return self.render_get_with_error("Nenhuma ordem encontrada com os dados informados.")
            if order["order_nfse_status"] != "not_issued":
                return self.render_get_with_error("A ordem não se encontra em um estado de not_issued.")
            if order["order_status"] != "paid":
                return self.render_get_with_error("A ordem não se encontra paga para emitir a NFSE.")
            refunded_user = self.load_user(self.post["user_email"])
            if not refunded_user:
                return self.render_get_with_error("Nenhum usuário encontrado como dono da ordem.")
            BillingController().generate_bill_of_sale(refunded_user, order)
            return self.render_get_with_error("Tentativa de emitir nota fiscal concluída.")

        if self.post.get("command") == "re_issue_order_nfse_pdf":
            order = Dynamo().get_order(self.post["order_id"])
            if not order:
                return self.render_get_with_error("Nenhuma ordem encontrada com os dados informados.")
            if order["order_status"] != "paid":
                return self.render_get_with_error("A ordem não se encontra paga para emitir a NFSE em PDF.")
            BillingController().generate_only_pdf_nfse(order)
            return self.render_get_with_error("Tentativa de emitir nota fiscal em PDF concluída.")

        if self.post.get("command") == "refund_order":
            order = Dynamo().get_order(self.post["order_id"])
            if not order:
                return self.render_get_with_error("Nenhuma ordem encontrada com os dados informados.")
            if order["order_status"] != "paid":
                return self.render_get_with_error("A ordem não se encontra paga para realizar reembolso.")
            if order["order_status"] != "card":
                return self.render_get_with_error("Só é possível reembolsar ordens do tipo cartão de crédito.")
            if not check_if_order_is_in_refund_time(order["created_at"]):
                return self.render_get_with_error("A ordem já excedeu o tempo máximo de pedido de reembolso.")
            refunded_user = self.load_user(order["order_user_id"])
            if not refunded_user:
                return self.render_get_with_error("Nenhum usuário encontrado como dono da ordem.")

            stripe_refund_response = StripeController().refunded_order(order["order_payment_stripe_charge_id"])
            if stripe_refund_response.get("status") == "succeeded":
                Dynamo().update_entity(order, "order_status", "refunded")
                if order["order_nfse_status"] == "issued":
                    BillingController().refund_bill_of_sale(order)
                if order["order_currency"] == "usd":
                    BillingController().cancel_international_pdf_bill_of_sale(order)
                if order["order_type"] == "unique":
                    raise Exception("TODO")
                else:
                    if order["order_payment_stripe_subscription_id"] == refunded_user.user_subscription_id:
                        refunded_user.cancel_current_subscription(valid_until_now=True)
                self.send_refund_order_email(refunded_user.user_email, order["order_id"])
                return self.render_get_with_error("Pagamento Stripe reembolsado com sucesso.")

            # elif self.utils.check_if_order_is_from_backoffice(order["order_payment_service"]):
            #     Dynamo().update_entity(order, "order_status", "refunded")
            #     if order["order_nfse_status"] == "issued":
            #         BillingController().refund_bill_of_sale(order)
            #     if order["order_type"] == "unique":
            #         refunded_user.spend_credits(order["order_total_credits"], order["order_id"], "order_refund", order.get("order_is_booth"))
            #     self.send_refund_order_email(refunded_user.user_email, order["order_id"])
            #     return self.render_get_with_error("Pagamento Backoffice reembolsado com sucesso.")
        return self.render_get()

    def send_refund_order_email(self, user_email, order_id):
        html = ReadWrite().read_html("backoffice_orders/_codes/html_email_order_refund")
        html.esc("order_id_val", order_id)
        Ses().send_email(user_email, body_html=str(html), body_text=str(html), subject_data="Augin - " + self.translate("Sua compra está sendo reembolsada"))
