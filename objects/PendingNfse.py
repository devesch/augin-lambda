from time import time


class PendingNfse:
    def __init__(self, pending_nfse_order_id="", pending_nfse_order_user_id="") -> None:
        self.pk = "pendingnfse#" + pending_nfse_order_id
        self.sk = str(time())
        self.pending_nfse_order_user_id = pending_nfse_order_user_id
        self.pending_nfse_order_id = pending_nfse_order_id
        self.created_at = str(time())
        self.entity = "pending_nfse"
