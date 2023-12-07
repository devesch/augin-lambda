from utils.Config import lambda_constants
from utils.AWS.S3 import S3
import traceback
import json

ses_client = None
us_ses_client = None


class Ses:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Ses, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def send_email_with_attachment(self, email_destination, email_subject, email_text, attachment_file_name, email_attachment_bucket, email_attachment_key, region=lambda_constants["region"]):
        import os
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication

        attachment_path = f"{lambda_constants['tmp_path']}{attachment_file_name}"
        S3().download_file(email_attachment_bucket, email_attachment_key, attachment_path)

        ToAddresses = []
        if type(email_destination) == list:
            ToAddresses = email_destination
        else:
            ToAddresses = [email_destination]

        msg = MIMEMultipart("mixed")
        msg["Subject"] = email_subject
        msg["From"] = lambda_constants["email_sender"]
        msg["To"] = ", ".join(ToAddresses)
        msg_body = MIMEMultipart("alternative")
        textpart = MIMEText(email_text.encode("utf-8"), "plain", "utf-8")
        htmlpart = MIMEText(email_text.encode("utf-8"), "html", "utf-8")
        msg_body.attach(textpart)
        msg_body.attach(htmlpart)
        with open(attachment_path, "rb") as attachment_file:
            attachment = MIMEApplication(attachment_file.read())
            attachment.add_header("Content-Disposition", "attachment", filename=os.path.basename(attachment_path))
        msg.attach(msg_body)
        msg.attach(attachment)

        if region == "us-east-1":
            ses_client = self.get_us_ses_client()
        else:
            ses_client = self.get_ses_client()

        response = ses_client.send_raw_email(
            Source=lambda_constants["email_sender"],
            Destinations=ToAddresses,
            RawMessage={
                "Data": msg.as_string(),
            },
            ConfigurationSetName="Config",
        )
        return response

    def send_error_email(self, event, function, error, email_destination=["eugenio@devesch.com.br", "matheus@devesch.com.br"], region=lambda_constants["region"]):
        try:
            tb = traceback.format_exc()
        except:
            tb = "Não ocorreu"
        try:
            body_html = f"ERROR {function.upper()}: {error}\n\n<br><br> TRACEBACK: {tb}\n\n<br><br> EVENT: {json.dumps(event)}"
        except:
            body_html = f"ERROR {function.upper()}: {error}\n\n<br><br> TRACEBACK: {tb}\n\n<br><br> EVENT: {str(event.__dict__)}"

        return self.send_email(email_destination, body_html, body_html, subject_data=f"ERROR {function.upper()}", region=region)

    def send_email_simple(self, email_destination, body_html="", region=lambda_constants["region"]):
        return self.send_email(email_destination, body_html, body_html, body_html, region)

    def send_email(self, email_destination, body_html="", body_text="", subject_data="", region=lambda_constants["region"]):
        ToAddresses = []
        if type(email_destination) == list:
            ToAddresses = email_destination
        else:
            ToAddresses = [email_destination]

        if region == "us-east-1":
            ses_client = self.get_us_ses_client()
        else:
            ses_client = self.get_ses_client()

        ses_client.send_email(
            Destination={"ToAddresses": ToAddresses},
            Message={
                "Body": {
                    "Html": {
                        "Charset": "utf-8",
                        "Data": str(body_html),
                    },
                    "Text": {
                        "Charset": "utf-8",
                        "Data": str(body_text),
                    },
                },
                "Subject": {
                    "Charset": "utf-8",
                    "Data": subject_data,
                },
            },
            Source=f"Augin <{lambda_constants['email_sender']}>",
            ConfigurationSetName="Config",
        )
        return True

    def get_us_ses_client(self):
        global us_ses_client
        if us_ses_client:
            return us_ses_client
        import boto3

        us_ses_client = boto3.client("ses", region_name="us-east-1")
        return us_ses_client

    def get_ses_client(self):
        global ses_client
        if ses_client:
            return ses_client
        import boto3

        ses_client = boto3.client("ses", region_name=lambda_constants["region"])
        return ses_client
