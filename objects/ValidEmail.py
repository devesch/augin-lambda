import time


class ValidEmail:
    def __init__(self, email) -> None:
        self.pk = "valid_email#" + email
        self.sk = "valid_email#" + email
        self.created_at = str(time.time())
        self.entity = "valid_email"
