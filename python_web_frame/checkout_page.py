from python_web_frame.base_page import BasePage

# from utils.Config import lambda_constants
# from utils.utils.Sort import Sort
# from utils.utils.ReadWrite import ReadWrite
# from utils.utils.Generate import Generate
# from utils.AWS.Dynamo import Dynamo
# from utils.AWS.S3 import S3
# from python_web_frame.controllers.model_controller import ModelController
# from objects.User import sort_user_folders


class CheckoutPage(BasePage):
    def __init__(self) -> None:
        super().__init__()
