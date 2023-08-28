import os
import json
from utils.Config import lambda_constants

sqs_client = None


class Sqs:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Sqs, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def send_message(self, queue_url, message_json, message_attributes=False):
        if not message_attributes:
            response = self.get_sqs_client().send_message(QueueUrl=queue_url, MessageBody=json.dumps(message_json))
        else:
            response = self.get_sqs_client().send_message(QueueUrl=queue_url, MessageBody=json.dumps(message_json), MessageAttributes=message_attributes)
        return response

    def receive_message(self, queue_url, max_number_of_messages=10, visibility_timeout=120):
        response = self.get_sqs_client().receive_message(QueueUrl=queue_url, MaxNumberOfMessages=max_number_of_messages, VisibilityTimeout=visibility_timeout)
        messages = []
        if "Messages" in response:
            for message in response["Messages"]:
                message["Body"] = json.loads(message["Body"])
                messages.append(message)
        return messages

    def delete_message(self, queue_url, receipt_handle):
        self.get_sqs_client().delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        if not os.environ.get("AWS_EXECUTION_ENV") is None:
            print("Message deleted from SQS queue.")

    def get_sqs_client(self):
        global sqs_client
        if sqs_client:
            return sqs_client
        import boto3

        sqs_client = boto3.client("sqs", region_name=lambda_constants["region"])
        return sqs_client
