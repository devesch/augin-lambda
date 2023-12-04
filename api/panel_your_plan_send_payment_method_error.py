from python_web_frame.panel_page import PanelPage
from utils.AWS.Ses import Ses

class PanelYourPlanSendPaymentMethodError(PanelPage):
    def run(self, event, error):
        Ses().send_error_email(event, "panel_your_plan_send_payment_method_error", error, email_destination="matheus@devesch.com.br")