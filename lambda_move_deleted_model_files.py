import json
import os
from utils.AWS.S3 import S3
from utils.AWS.Ses import Ses
from utils.Config import lambda_constants


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as error:
        Ses().send_error_email(event, "lambda_move_deleted_model_files", error, region="us-east-1")


def main_lambda_handler(event, context):
    model_upload_path = event.get("model_upload_path")
    model_state = event.get("model_state")

    if model_state == "completed":
        S3().copy_folder_from_one_bucket_to_another(lambda_constants["processed_bucket"], lambda_constants["archive_bucket"], model_upload_path, model_upload_path)
    S3().delete_folder(lambda_constants["processed_bucket"], model_upload_path)
    return {"success": model_upload_path + " changed buckets"}


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow_move_deleted_model_files.json", "r") as read_file:
        event = json.load(read_file)
        html = main_lambda_handler(event, None)
