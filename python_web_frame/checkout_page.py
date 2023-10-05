from python_web_frame.base_page import BasePage
from utils.utils.ReadWrite import ReadWrite

# from utils.Config import lambda_constants
# from utils.utils.Sort import Sort
# from utils.utils.Generate import Generate
# from utils.AWS.Dynamo import Dynamo
# from utils.AWS.S3 import S3
# from python_web_frame.controllers.model_controller import ModelController
# from objects.User import sort_user_folders


class CheckoutPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

    def show_html_add_coupon_button(self):
        html = ReadWrite().read_html("checkout_stripe_subscription/_codes/html_add_coupon_button")
        return str(html)

    def show_html_remove_coupon_button(self):
        html = ReadWrite().read_html("checkout_stripe_subscription/_codes/html_remove_coupon_button")
        return str(html)
