from utils.Config import Config, lambda_constants
from utils.utils.ReadWrite import ReadWrite
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Sqs import Sqs
from utils.AWS.Ses import Ses
from utils.AWS.S3 import S3
import json
import time
import os

### CAREFUL FUNCTION ALSO USED ON INTEGRATEBIM ###


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as error:
        Ses().send_error_email(event, "AUGIN lambda_web_data_process_json", error, region="us-east-1")


def main_lambda_handler(event, context):
    print(json.dumps(event))
    start_time = time.time()
    Config().update_lambda_contants("web-data")
    Dynamo().update_dynamo_constants()
    for record in event["Records"]:
        record["Body"] = json.loads(record["body"].replace("'", '"'))
        current_index = record["Body"]["key"].split("_jsons_parts_")[1].split("-")[0]
        end_index = record["Body"]["key"].split("_jsons_parts_")[1].split("-")[1].split(".json")[0]
        if current_index == "1":
            email_text = "Starting project " + current_index + "/" + end_index + " at " + str(time.time())
            # Ses().send_email_simple("eugenio@devesch.com.br", email_text, region="us-east-1")

        S3().download_file(record["Body"]["bucket"], record["Body"]["key"], lambda_constants["tmp_path"] + "_json_5000.json")
        json_5000 = ReadWrite().read_json(lambda_constants["tmp_path"] + "_json_5000.json")
        total_items = json_5000["files"]

        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_item = {executor.submit(Dynamo().put_entity(item, table="web-data")): item for item in total_items}
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    future.result()
                except Exception as exc:
                    print(f"Putting item {item} generated an exception: {exc}")
        S3().delete_file(record["Body"]["bucket"], record["Body"]["key"])
        Sqs().delete_message(lambda_constants["sqs_queue_url_json5000"], record["receiptHandle"])
        ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])
        if current_index == end_index:
            email_text = "Ending project " + current_index + "/" + end_index + " at " + str(time.time())
            # Ses().send_email_simple("eugenio@devesch.com.br", email_text, region="us-east-1")

    total_time = time.time() - start_time
    return {"success": current_index + " part processed to dynamoDB, TOTAL TIME: " + str(total_time)}


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow_lambda_web_data_process_json.json", "r") as read_file:
        event = json.load(read_file)
        html = main_lambda_handler(event, None)
