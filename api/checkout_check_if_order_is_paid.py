from python_web_frame.checkout_page import CheckoutPage
from utils.AWS.Dynamo import Dynamo


class CheckoutCheckIfOrderIsPaid(CheckoutPage):
    def run(self):
        if not self.user:
            return {"error": "Nenhum usuário encontrado"}
        if not self.post.get("order_id"):
            return {"error": "Nenhuma order_id enviada"}
        order = Dynamo().get_order(self.post["order_id"])
        if not order:
            return {"error": "Nenhuma order encontrada."}
        if order["order_status"] != "paid":
            return {"error": "Ordem encontrada porém não se encontra paga"}
        return {"success": "Ordem paga"}
