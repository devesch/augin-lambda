from objects.UserDevice import disconnect_device, generate_connected_and_disconnected_devices, generate_disconnected_devices_in_last_30d
from python_web_frame.controllers.stripe_controller import StripeController
from python_web_frame.controllers.model_controller import ModelController
from objects.BackofficeData import increase_backoffice_data_total_count
from objects.UserFolder import check_if_folder_movement_is_valid
from objects.CancelSubscription import CancelSubscription
from objects.UserPaymentMethod import UserPaymentMethod
from python_web_frame.panel_page import PanelPage
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.Generate import Generate
from python_web_frame.user_page import UserPage
from utils.utils.Validation import Validation
from utils.utils.Generate import Generate
from utils.Config import lambda_constants
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Lambda import Lambda
from objects.User import load_user
from utils.AWS.S3 import S3
import time


class UpdateOrder(UserPage, PanelPage):
    def run(self):
        if not self.post.get("command"):
            return {"error": "Nenhum command no post"}
        if not self.user:
            return {"error": "Nenhum usuário encontrado"}
        if not self.post.get("order_id"):
            return {"error": "Nenhuma order_id enviada no post"}
        order = Dynamo().get_order(self.post["order_id"])
        if not order:
            return {"error": "Nenhuma order encontrada com a order_id enviada no post"}

        if order["order_user_id"] != self.user.user_id and self.user.user_crendential != "admin":
            return {"error": "Esta ordem não pertence ao usuário"}

        return getattr(self, self.post["command"])(order)

    def generate_page_pdf_download_link(self, order):
        order_pdf_id = Generate().generate_short_id()
        lambda_generate_pdf_response = Lambda().invoke("lambda_generate_pdf", "RequestResponse", {"input_url": lambda_constants["original_domain_name_url"] + "/panel_order/?order_id=" + order["order_id"] + "&not_render_menu=True", "output_bucket": lambda_constants["processed_bucket"], "output_key": "order_pdf_pages/" + order["order_id"] + "/" + order_pdf_id + ".pdf"})
        if "error" in lambda_generate_pdf_response:
            raise Exception("ERROR IN lambda_generate_pdf " + lambda_constants["original_domain_name_url"])
        return {"success": "Link do download gerado com sucesso", "pdf_download_link": lambda_constants["processed_bucket_cdn"] + "/order_pdf_pages/" + order["order_id"] + "/" + order_pdf_id + ".pdf"}
