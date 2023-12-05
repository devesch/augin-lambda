from python_web_frame.panel_page import PanelPage
from utils.AWS.Ses import Ses
from utils.Config import lambda_constants

class SendErrorEmail(PanelPage):
    def run(self):
        if not self.post.get("error"):
            return {"error": "Nenhum erro enviado no post"}
        if not self.post.get("email_destination"):
            return {"error": "Nenhum email de destino enviado no post"}
        Ses().send_error_email(self.event, lambda_constants["domain_name"] + str(event.get_prefix()) + " pages lambda", self.post["error"],  self.post["email_destination"])
        return {"success": "Email de erro enviado com sucesso"}