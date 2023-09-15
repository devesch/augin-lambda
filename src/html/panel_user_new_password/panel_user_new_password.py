from python_web_frame.panel_page import PanelPage


class PanelUserNewPassword(PanelPage):
    name = "Painel - Nova Senha do Usuário"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        html.esc("user_email_val", self.user.user_email)
        if self.post.get("user_current_password"):
            html.esc("user_current_password_val", self.post["user_current_password"])
        if self.post.get("user_password"):
            html.esc("user_password_val", self.post["user_password"])
        return str(html)

    def render_post(self):
        # TODO: como vai ficar a tradução aqui nessas mensagens hardcoded?
        if not self.post.get("user_current_password"):
            return self.render_get_with_error("Por favor informe a senha atual.")
        if not self.user.check_if_password_is_corrected(self.post["user_current_password"]):
            return self.render_get_with_error("A senha atual está incorreta.")
        if not self.post.get("user_password"):
            return self.render_get_with_error("Por favor informe uma senha.")
        if not self.post.get("user_password_confirm"):
            return self.render_get_with_error("Por favor confirme sua senha.")
        if not self.utils.validate_password(self.post["user_password"]):
            return self.render_get_with_error("A senha deve ter entre 8 e 45 caracteres.")

        self.user.update_password(self.post["user_password"], self.utils.generate_salt(9))
        self.user.user_ip = self.event.get_user_ip()
        self.dynamo.put_entity(self.user.__dict__)
        self.user.clear_all_auth_tokens()
        self.send_email_user_password_modified(self.user.user_email, self.user.user_name)
        return {"html": self.utils.redirect("home"), "command": "logout", "user_auth_token": None}

    def send_email_user_password_modified(self, user_email, user_name):
        try:
            html = self.utils.read_html("panel_user_new_password/_codes/html_password_modified_email")
            html.esc("user_name_val", user_name)
            get_ses_client().send_email(
                Destination={"ToAddresses": [user_email]},
                Message={
                    "Body": {
                        "Html": {
                            "Charset": "utf-8",
                            "Data": str(html),
                        },
                        "Text": {
                            "Charset": "utf-8",
                            "Data": str(html),
                        },
                    },
                    "Subject": {
                        "Charset": "utf-8",
                        "Data": "Magipix - Sua senha foi alterada",
                    },
                },
                Source=lambda_constants["email_sender"],
                ConfigurationSetName="configset",
            )
            return True
        except:
            return False
