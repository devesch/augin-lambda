from time import time


class BackofficeData:
    def __init__(self) -> None:
        self.pk = "backoffice#"
        self.sk = "backoffice#"
        self.backoffice_data_total_user_count = "0"
        self.backoffice_data_total_order_count = "0"
        self.backoffice_data_total_model_count = "0"
        self.backoffice_data_total_page = {}
        self.created_at = str(time())
        self.entity = "backoffice_data"
