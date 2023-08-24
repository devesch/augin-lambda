import time


class UserAuthToken:
    def __init__(self, user_auth_token, auth_user_email) -> None:
        self.pk = "auth#" + user_auth_token
        self.sk = "auth#" + user_auth_token
        self.auth_user_email = auth_user_email
        self.created_at = str(time.time())
        self.entity = "auth_token"
