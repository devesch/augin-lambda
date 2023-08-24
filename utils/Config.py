import os
import json

if not os.environ.get("AWS_EXECUTION_ENV") is None:
    domain_name = os.environ["domain_name"]
    prefix_name = os.environ["prefix_name"]
    sufix_name = os.environ["sufix_name"]
    region = os.environ["region"]
    kms_key_id = os.environ["kms_key_id"]
    s3_put_user_key_id = os.environ["s3_put_user_key_id"]
    s3_put_user_secret_access_key = os.environ["s3_put_user_secret_access_key"]
    tmp_path = "/tmp/"
    ifc_converter = "LinuxIfcConvert"

else:
    with open(".vscode/enviroment_variables.json", "r", encoding="utf-8") as read_file:
        env_var = json.load(read_file)
        domain_name = env_var["domain_name"]
        prefix_name = env_var["prefix_name"]
        sufix_name = env_var["sufix_name"]
        region = env_var["region"]
        kms_key_id = env_var["kms_key_id"]
        s3_put_user_key_id = env_var["s3_put_user_key_id"]
        s3_put_user_secret_access_key = env_var["s3_put_user_secret_access_key"]
        tmp_path = "tmp/"
        ifc_converter = "IfcConvert.exe"


base_url = f"https://{prefix_name}{domain_name}{sufix_name}"
cdn_bucket = "cdn." + domain_name + sufix_name
cdn_base_url = "https://" + cdn_bucket


lambda_constants = {
    "ifc_converter": ifc_converter,
    "s3_put_user_key_id": s3_put_user_key_id,
    "s3_put_user_secret_access_key": s3_put_user_secret_access_key,
    "email_sender": "eugenio@devesch.com.br",
    "cloudfront_img_resizer": "",
    "sqs_queue_url_json5000": "https://sqs.sa-east-1.amazonaws.com/847154778207/web-data-5000-json",
    "sqs_queue_url_process_xml_to_dynamo": "https://sqs.sa-east-1.amazonaws.com/847154778207/process_xml_to_dynamo",
    "sqs_queue_url_process_in_ec2": "https://sqs.sa-east-1.amazonaws.com/847154778207/ifc-ec2-process",
    "stepfunction_arn": "arn:aws:states:sa-east-1:847154778207:stateMachine:IFC-processor-state-machine",
    "prefix_name": prefix_name,
    "sufix_name": sufix_name,
    "domain_name": domain_name,
    "domain_name_url": base_url,
    "table_web_data": "web-data",
    "table_project": domain_name,
    "region": region,
    "cdn_bucket": cdn_bucket,
    "cdn": cdn_base_url,
    "upload_bucket": f"upload.{domain_name}{sufix_name}",
    "processed_bucket": f"processed.{domain_name}{sufix_name}",
    "processed_bucket_cdn": f"https://processed.{domain_name}{sufix_name}",
    "current_language": "pt",
    "tmp_path": tmp_path,
    "kms_key_id": kms_key_id,
    "pagination_size": "100",
}


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def update_lambda_contants(self, prefix, post):
        global lambda_constants

        if "pagination_size" in post:
            if int(post.get("pagination_size")) > 2 and int(post.get("pagination_size")) < 1000:
                lambda_constants["pagination_size"] = post["pagination_size"]

        if "dev" in prefix:
            global base_url
            global cdn_bucket
            global cdn_base_url
            global prefix_name

            prefix_name = "dev-tqs."
            base_url = f"https://{prefix_name}{domain_name}{sufix_name}"
            cdn_bucket = prefix_name.replace(".", "-cdn.") + domain_name + sufix_name
            cdn_base_url = "https://" + cdn_bucket

            lambda_constants["prefix_name"] = prefix_name
            lambda_constants["domain_name_url"] = base_url
            lambda_constants["table_web_data"] = f"web-data"
            lambda_constants["table_project"] = f"{domain_name}-dev"
            lambda_constants["region"] = region
            lambda_constants["cdn_bucket"] = cdn_bucket
            lambda_constants["cdn"] = cdn_base_url

    def get_region(self):
        if os.environ.get("AWS_EXECUTION_ENV") is None:
            with open(".vscode/enviroment_variables.json", "r", encoding="utf-8") as read_file:
                env_var = json.load(read_file)
                return env_var["region"]
        else:
            import boto3

            session = boto3.session.Session()
            return session.region_name