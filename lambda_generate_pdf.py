import json
import os
import pdfkit
from utils.AWS.Ses import Ses
from utils.AWS.S3 import S3


def main_lambda_handler(event, context):
    print(json.dumps(event))

    if os.environ.get("AWS_EXECUTION_ENV") is None:
        pdf_path = "tmp/nfse.pdf"
        PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf="wkhtmltopdf")
    else:
        pdf_path = "/tmp/nfse.pdf"
        PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf="/opt/bin/wkhtmltopdf")

    pdfkit.from_url(event["input_url"], pdf_path, configuration=PDFKIT_CONFIG)

    S3().upload_file(event["output_bucket"], event["output_key"], pdf_path)
    return {"success": "nfse generated for " + event["output_key"]}


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as e:
        Ses().send_error_email(event, "AUGIN lambda_generate_pdf", e)
        return {"error": "error running lambda_generate_pdf"}


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow_lambda_generate_pdf.json", "r") as read_file:
        event = json.load(read_file)
        html = main_lambda_handler(event, None)
        print("end")
