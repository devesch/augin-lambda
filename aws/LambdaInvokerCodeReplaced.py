import json
import os
from boto3 import client


def get_object_from_event(event):
    if "rawPath" in event:
        return event["rawPath"].split("/")[1]
    print("ERROR: Cannot rawPath in event")
    return None


def get_method_from_event(event):
    if "requestContext" in event:
        if "http" in event["requestContext"]:
            if "method" in event["requestContext"]["http"]:
                return event["requestContext"]["http"]["method"]
            print("ERROR: method not found in http")
            return None
        print("ERROR: http not found in requestContext")
        return None
    print("ERROR: requestContext not found in event")
    return None


last_post_event = ""
last_post_page = ""


def lambda_handler(event, context):
    lambda_client = client("lambda", region_name="sa-east-1")
    print(json.dumps(event))
    r = lambda_client.invoke(FunctionName="arn:aws:lambda:sa-east-1:260093079654:function:julianalaux", InvocationType="RequestResponse", Payload=json.dumps(event))
    payload = r["Payload"].read().decode()
    # print(str(payload))
    response = json.loads(payload)
    for p in response.keys():
        print(str(p))
    if "errorMessage" in payload:
        return {"statusCode": 200, "body": str(json.dumps(event)) + "<separetor> \n\n errorMessage_on_invoker: " + str((payload))}
    body = ""
    if "body" in response:
        body = response["body"]
        headers = ""
        if "headers" in response:
            headers = response["headers"]
        method = get_method_from_event(event)
        page = get_object_from_event(event)
        if str(method).upper() == "POST":
            global last_post_event
            global last_post_page
            last_post_event = event
            last_post_page = page
        show_page = None
        if page:
            show_page = page
        print("HEADERS:" + str(headers))
        return {"statusCode": 200, "headers": headers, "body": str(body)}
    else:
        return response


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow.json", "r") as read_file:
        event = json.load(read_file)
        print(lambda_handler(event, None))
    print("END")
