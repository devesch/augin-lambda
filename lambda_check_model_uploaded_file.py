from python_web_frame.controllers.model_controller import ModelController
from utils.AWS.Ses import Ses
from utils.AWS.Dynamo import Dynamo
from objects.User import load_user
import os
import json


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as error:
        Ses().send_error_email(event, "AUGIN lambda_check_model_uploaded_file", error, region="us-east-1")


def main_lambda_handler(event, context):
    uploaded_file = Dynamo().get_uploaded_file(event["uploaded_file_id"])
    uploaded_file["uploaded_file_response"] = ModelController().check_if_file_uploaded_is_valid(uploaded_file["uploaded_file_post"]["key"], uploaded_file["uploaded_file_post"]["original_name"], load_user(uploaded_file["uploaded_file_user_id"]))
    Dynamo().put_entity(uploaded_file)
    return {"success": "File check completed"}


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow_lambda_check_model_uploaded_file.json", "r") as read_file:
        event = json.load(read_file)
        lambda_handler(event, None)
