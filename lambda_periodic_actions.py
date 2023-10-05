from utils.Config import lambda_constants
from utils.utils.Http import Http
from utils.AWS.Ses import Ses
import os
import json


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as error:
        Ses().send_error_email(event, "AUGIN lambda_periodic_actions", error, region="us-east-1")


def main_lambda_handler(event, context):
    print("Running periodic_actions")
    response = Http().request("POST", lambda_constants["domain_name_url"] + "/api/lambda_periodic_actions", headers={}, data={"lambda_periodic_actions_key": lambda_constants["lambda_periodic_actions_key"]})
    return


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow.json", "r") as read_file:
        event = json.load(read_file)
        lambda_handler(event, None)
