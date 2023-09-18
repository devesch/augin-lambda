import json
import os
import traceback
import pdfkit
from boto3 import client

ses_client = client("ses")
s3_client = client("s3")


def respond(status, message):
    return {"statusCode": 200, "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, "body": json.dumps({status: message})}


def main_lambda_handler(event, context):

    print(json.dumps(event))

    if not event.get("input_url"):
        return respond("error", "no input_url in event")
    if not event.get("output_bucket"):
        return respond("error", "no output_bucket in event")
    if not event.get("output_key"):
        return respond("error", "no output_key in event")

    if os.environ.get("AWS_EXECUTION_ENV") is None:
        pdf_path = "tmp/nfse.pdf"
        PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf="wkhtmltopdf")
    else:
        pdf_path = "/tmp/nfse.pdf"
        PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf="/opt/bin/wkhtmltopdf")

    pdfkit.from_url(event["input_url"], pdf_path, configuration=PDFKIT_CONFIG)

    s3_client.upload_file(pdf_path, event["output_bucket"], event["output_key"])
    return respond("success", "nfse generated for " + event["output_key"])


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as e:
        send_error_email(event, "AUGIN lambda_generate_pdf", e)
        return respond("error", "error running lambda_generate_pdf")


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow.json", "r") as read_file:
        event = json.load(read_file)
        html = main_lambda_handler(event, None)
        print("end")


def send_error_email(event, function, error):
    try:
        tb = traceback.format_exc()
    except:
        tb = "Não ocorreu"
    try:
        html = "LAMBDA ERROR IN PROJECT " + function.upper() + ": " + str(error) + "\n\n<br><br> TRACEBACK: " + tb + "\n\n<br><br> EVENT: " + json.dumps(event)
    except:
        html = "LAMBDA ERROR IN PROJECT " + function.upper() + ": " + str(error) + "\n\n<br><br> TRACEBACK: " + tb + "\n\n<br><br> EVENT: " + str(event.__dict__)
    ses_client.send_email(
        Destination={"ToAddresses": ["eugenio@devesch.com.br"]},
        Message={
            "Body": {
                "Html": {
                    "Charset": "utf-8",
                    "Data": str(html),
                },
                "Text": {
                    "Charset": "utf-8",
                    "Data": str(html),
                },
            },
            "Subject": {
                "Charset": "utf-8",
                "Data": "LAMBDA ERROR IN PROJECT",
            },
        },
        Source="eugenio@devesch.com.br",
        ConfigurationSetName="configset",
    )
    return
