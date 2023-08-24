class UserPassword:
    def __init__(self, user_email, user_password, user_salt) -> None:
        self.pk = "user#" + user_email
        self.sk = "pass#" + user_email
        self.user_password = user_password
        self.user_salt = user_salt
