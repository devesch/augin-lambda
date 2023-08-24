from time import time


class VerifyEmail:
    def __init__(self, user_email, verify_email_code) -> None:
        self.pk = "user#" + user_email
        self.sk = "verify_email#" + verify_email_code
        self.verify_email_user_email = user_email
        self.verify_email_code = verify_email_code
        self.created_at = str(time())
        self.entity = "verify_email"
