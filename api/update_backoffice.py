from python_web_frame.backoffice_page import BackofficePage
from python_web_frame.controllers.billing_controller import BillingController
from python_web_frame.controllers.stripe_controller import StripeController
from objects.Order import check_if_order_is_in_refund_time
from utils.AWS.Dynamo import Dynamo


class UpdateBackoffice(BackofficePage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "Nenhum command no post"}
        if not self.user:
            return {"error": "Nenhum usuário encontrado"}
        if not self.user.user_credential == "admin":
            return {"error": "Este usuário não possui as credenciais para realizar este comando"}

        return getattr(self, self.post["command"])()

    def refund_order(self):
        order = Dynamo().get_order(self.post["order_id"])
        if not order:
            return {"error": "Nenhuma ordem encontrada com os dados informados"}
        if order["order_status"] != "paid":
            return {"error": "A ordem não se encontra paga para realizar reembolso"}
        if order["order_payment_method"] != "card":
            return {"error": "Só é possível reembolsar ordens do tipo cartão de crédito"}
        if not check_if_order_is_in_refund_time(order["created_at"]):
            return {"error": "A ordem já excedeu o tempo máximo de pedido de reembolso"}
        refunded_user = self.load_user(order["order_user_id"])
        if not refunded_user:
            return {"error": "Nenhum usuário encontrado como dono da ordem"}

        stripe_refund_response = StripeController().refunded_order(order["order_payment_stripe_charge_id"])
        if stripe_refund_response.get("status") != "succeeded":
            return {"success": "Não foi possível reembolsar a ordem no stripe"}
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
        return {"success": "Pagamento Stripe reembolsado com sucesso"}

    def re_issue_order_nfse_pdf(self):
        order = Dynamo().get_order(self.post["order_id"])
        if not order:
            return {"error": "Nenhuma ordem encontrada com os dados informados"}
        if order["order_status"] != "paid":
            return {"error": "A ordem não se encontra paga para emitir a NFSE em PDF"}
        BillingController().generate_only_pdf_nfse(order)
        return {"success": "Tentativa de emitir nota fiscal em PDF concluída"}

    def re_issue_order_nfse(self):
        order = Dynamo().get_order(self.post["order_id"])
        if not order:
            return {"error": "Nenhuma ordem encontrada com os dados informados"}
        if order["order_nfse_status"] != "not_issued":
            return {"error": "A ordem não se encontra em um estado de not_issued"}
        if order["order_status"] != "paid":
            return {"error": "A ordem não se encontra paga para emitir a NFSE"}
        refunded_user = self.load_user(order["order_user_id"])
        if not refunded_user:
            return {"error": "Nenhum usuário encontrado como dono da ordem"}
        BillingController().generate_bill_of_sale(refunded_user, order)
        return {"success": "Tentativa de emitir nota fiscal concluída"}
