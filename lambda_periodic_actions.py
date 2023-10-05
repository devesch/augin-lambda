from utils.Config import lambda_constants
from utils.utils.Http import Http
import os
import json


def lambda_handler(event, context):
    response = Http().request("POST", lambda_constants["domain_name_url"] + "/api/lambda_periodic_actions", headers={}, data={"lambda_periodic_actions_key": lambda_constants["lambda_periodic_actions_key"]})
    return


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow.json", "r") as read_file:
        event = json.load(read_file)
        lambda_handler(event, None)
