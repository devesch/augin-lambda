import json
import os
from utils.AWS.S3 import S3
from utils.AWS.Ses import Ses
from utils.AWS.Dynamo import Dynamo
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Generate import Generate
from utils.Config import lambda_constants


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as error:
        Ses().send_error_email(event, "lambda_generate_folder_zip", error, region="us-east-1")


def main_lambda_handler(event, context):
    print(json.dumps(event))
    ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])

    folder = Dynamo().get_folder(event["folder_id"])
    root_download_folder = lambda_constants["tmp_path"] + folder["folder_name"]
    os.mkdir(root_download_folder)
    download_folder(root_download_folder, folder["folders"], folder["files"])
    ReadWrite().zip_folder(root_download_folder, lambda_constants["tmp_path"] + "zipped_folder.zip")
    zip_s3_key = "generated_folder_zips/" + Generate().generate_short_id() + ".zip"
    S3().upload_file(lambda_constants["processed_bucket"], zip_s3_key, lambda_constants["tmp_path"] + "zipped_folder.zip")

    return {"success": lambda_constants["processed_bucket_cdn"] + "/" + zip_s3_key}


def download_folder(local_path, folders, files):
    if files:
        for model_id in files:
            model = Dynamo().get_model_by_id(model_id)
            if model:
                S3().download_file(lambda_constants["processed_bucket"], model["model_upload_path_zip"], local_path + "/" + model["model_name"] + ".zip")
    if folders:
        for folder_id in folders:
            folder = Dynamo().get_folder(folder_id)
            if folder:
                root_download_folder = local_path + "/" + folder["folder_name"]
                os.mkdir(root_download_folder)
                download_folder(root_download_folder, folder["folders"], folder["files"])


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow_lambda_generate_folder_zip.json", "r") as read_file:
        event = json.load(read_file)
        html = main_lambda_handler(event, None)
