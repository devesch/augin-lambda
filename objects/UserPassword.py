class UserPassword:
    def __init__(self, user_id, user_password, user_salt) -> None:
        self.pk = "user#" + user_id
        self.sk = "pass#" + user_id
        self.user_password = user_password
        self.user_salt = user_salt
