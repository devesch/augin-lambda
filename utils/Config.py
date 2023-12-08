import os
import json

if not os.environ.get("AWS_EXECUTION_ENV") is None:
    domain_name = os.environ["domain_name"]
    prefix_name = os.environ["prefix_name"]
    sufix_name = os.environ["sufix_name"]
    region = os.environ["region"]
    kms_key_id = os.environ["kms_key_id"]
    s3_put_user_key_id = os.environ.get("s3_put_user_key_id")
    s3_put_user_secret_access_key = os.environ.get("s3_put_user_secret_access_key")
    tmp_path = "/tmp/"

else:
    with open(".vscode/enviroment_variables.json", "r", encoding="utf-8") as read_file:
        env_var = json.load(read_file)
        domain_name = env_var["domain_name"]
        prefix_name = env_var["prefix_name"]
        sufix_name = env_var["sufix_name"]
        region = env_var["region"]
        kms_key_id = env_var["kms_key_id"]
        s3_put_user_key_id = env_var.get("s3_put_user_key_id")
        s3_put_user_secret_access_key = env_var.get("s3_put_user_secret_access_key")
        tmp_path = "tmp/"

base_url = f"https://{prefix_name}{domain_name}{sufix_name}"
cdn_bucket = "cdn." + domain_name + sufix_name
cdn_base_url = "https://" + cdn_bucket
css_js_location = cdn_base_url
original_domain_name_url = base_url

if os.environ.get("AWS_EXECUTION_ENV") is None and os.getenv("LOCAL_SERVER"):
    base_url = f"http://127.0.0.1:3000"
    cdn_base_url = "/static"
    css_js_location = "/static/dist"

### TODO CHANGE CNPJ TO AUGIN
lambda_constants = {
    "project_name": "Augin",
    "hcaptcha_secret": "ES_1de692eba3a6418da02963406bee95f5",
    "hcaptcha_sitekey": "9cc05442-d6d0-45aa-9ac2-f4ce3d6f8b64",
    "wa_number": "51999859355",
    "zerobounce_apikey": "4c69c9e1231f4de6ac0ff78a8e505f17",
    "brand_api_endpoint": "https://api.branch.io/v1/",
    "branch_key": "key_live_kbPDVR9iW4fdsvi1MNpMRlnetqjvZogI",
    "ip_data_api_key": "6aa0e0c8249d4135172b977b137ee37adf36a0975f9e6367dbaa912a",
    "legalentity_api_key": "DchNkBsyXbdxG1uCh49IJrhw0bAf0rJguQ1udQQ1qAswkC4zodUYQvxJ4XBYS35s4Tz",
    "lambda_periodic_actions_key": "f30af33e-532d-45a2-8333-29cc408f1903",
    "pt_tawk_api_key": "33dae5dea7d222eefba9e1cae07a3cf74d2a9a27",
    "pt_tawk_api_code": "62068b389bd1f31184dc2cbd/1frkovm6f",
    "international_tawk_api_key": "894e92b708f45517819d0d81f933925ef35f74df",
    "international_tawk_api_code": "6206896f9bd1f31184dc2c83/1frkohnns",
    "mouse_flow_project_id": "278934d8-0711-49f8-9b58-9db2c8cf6f81",
    "company_name": "Augin",
    "company_short_address_val": "Av. Mariland 403, Sala 802",
    "company_full_address": "Av. Mariland 403, Sala 802 - Porto Alegre, RS",
    "company_formated_cnpj": "34.804.848/0001-95",
    "cnpj": "34804848000195",
    "phone": "51999859355",
    "municipal_inscription": "62586920",
    # "company_formated_cnpj": "31.758.054/0001-44",
    # "cnpj": "31758054000144",
    # "municipal_inscription": "61154822",
    "s3_put_user_key_id": s3_put_user_key_id,
    "s3_put_user_secret_access_key": s3_put_user_secret_access_key,
    "email_sender": "augin@augin.app",
    "cloudfront_img_resizer": "",
    "sqs_queue_url_json5000": "https://sqs.us-east-1.amazonaws.com/847154778207/web-data-5000-json",
    "sqs_queue_url_process_xml_to_dynamo": "https://sqs.us-east-1.amazonaws.com/847154778207/process_xml_to_dynamo",
    "sqs_queue_url_process_in_ec2": "https://sqs.us-east-1.amazonaws.com/847154778207/ifc-ec2-process",
    "stepfunction_arn": "arn:aws:states:us-east-1:847154778207:stateMachine:IFC-processor-state-machine",
    "lambda_generate_folder_zip": "generate_folder_zip",
    "lambda_move_deleted_model_files": "move_deleted_model_files",
    "lambda_check_model_uploaded_file": "check_model_uploaded_file",
    "maxium_ifc_project_filesize": "1073741824",
    "css_js_location": css_js_location,
    "prefix_name": prefix_name,
    "sufix_name": sufix_name,
    "domain_name": domain_name,
    "domain_name_url": base_url,
    "original_domain_name_url": original_domain_name_url,
    "table_web_data": "web-data",
    "table_project": domain_name,
    "region": region,
    "cdn_bucket": cdn_bucket,
    "cdn": cdn_base_url,
    "upload_bucket": f"upload.{domain_name}{sufix_name}",
    "processed_bucket": f"processed.{domain_name}{sufix_name}",
    "archive_bucket": f"archive.{domain_name}{sufix_name}",
    "processed_bucket_cdn": f"https://processed.{domain_name}{sufix_name}",
    "current_language": "pt",
    "tmp_path": tmp_path,
    "kms_key_id": kms_key_id,
    "available_categories": {
        "air_conditioning": {"category_id": "air_conditioning", "category_name": "Air Conditioning"},
        "architecture": {"category_id": "architecture", "category_name": "Architecture"},
        "electric": {"category_id": "electric", "category_name": "Electric"},
        "structural": {"category_id": "structural", "category_name": "Structural"},
        "executive": {"category_id": "executive", "category_name": "Executive"},
        "gas": {"category_id": "gas", "category_name": "Gas"},
        "hydraulics": {"category_id": "hydraulics", "category_name": "Hydraulics"},
        "fire": {"category_id": "fire", "category_name": "Fire"},
        "infrastructure": {"category_id": "infrastructure", "category_name": "Infrastructure"},
        "interiors": {"category_id": "interiors", "category_name": "Interiors"},
        "federated": {"category_id": "federated", "category_name": "Federated"},
        "others": {"category_id": "others", "category_name": "Others"},
    },
    "plan_reference_trackers": {"indisponível": "unavailable", "único": "unique", "múltiplo": "multiple"},
    "user_orders_page_size": "12",
    "free_plan_id": "ee15916d5acc",
}

devices = {
    "0a6c5368e8f8eadd46124b98bd1a3fac": {
        "device_id": "0a6c5368e8f8eadd46124b98bd1a3fac",
        "device_model": "samsung SM-G780G",
        "device_name": "S20 FE de Juan",
        "device_os": "Android OS 12 / API-31 (SP1A.210812.016/G780GXXS3BVB3)",
    },
    "28476a00666104fb7166395e4486a7d4": {
        "device_id": "28476a00666104fb7166395e4486a7d4",
        "device_model": "samsung SM-G780G",
        "device_name": "S20 FE de Juan",
        "device_os": "Android OS 12 / API-31 (SP1A.210812.016/G780GXXS3CVJ1)",
    },
    "2a6edd29ee0457cd563937e280e577cc": {
        "device_id": "2a6edd29ee0457cd563937e280e577cc",
        "device_model": "samsung SM-A125M",
        "device_name": "Galaxy A12 de Cristian",
        "device_os": "Android OS 12 / API-31 (SP1A.210812.016/A125MUBS3CVH3)",
    },
    "48bbbc3d6d2ad34cd2d5a0c980c3ef60": {
        "device_id": "48bbbc3d6d2ad34cd2d5a0c980c3ef60",
        "device_model": "samsung SM-S916U1",
        "device_name": "Juan's S23+",
        "device_os": "Android OS 13 / API-33 (TP1A.220624.014/S916U1UES1AWBM)",
    },
    "51dd07118cc1cd0b6bac06b9b51703bcfd74c63a": {
        "device_id": "51dd07118cc1cd0b6bac06b9b51703bcfd74c63a",
        "device_model": "System Product Name (ASUS)",
        "device_name": "DESKTOP-QN6LRVD",
        "device_os": "Windows 11  (10.0.22621) 64bit",
    },
    "51dd07118cc1cd0b6bac06b9b51703bcfd74c63a": {
        "device_id": "51dd07118cc1cd0b6bac06b9b51703bcfd74c63a",
        "device_model": "System Product Name (ASUS)",
        "device_name": "DESKTOP-QN6LRVD",
        "device_os": "Windows 11  (10.0.22621) 64bit",
    },
    "52c2dd9502490b6f1069b09143dde3e8": {
        "device_id": "52c2dd9502490b6f1069b09143dde3e8",
        "device_model": "samsung SM-S916U1",
        "device_name": "Juan's S23+",
        "device_os": "Android OS 13 / API-33 (TP1A.220624.014/S916U1UES1AWBM)",
    },
    "546af9e3fa01404def65a9a5fb1b9b186f8c449d": {
        "device_id": "546af9e3fa01404def65a9a5fb1b9b186f8c449d",
        "device_model": "System Product Name (System manufacturer)",
        "device_name": "DESKTOP-IIKVFSG",
        "device_os": "Windows 10  (10.0.19045) 64bit",
    },
    "75a3a0983e653e194be2cb6732ea44587edaa95e": {
        "device_id": "75a3a0983e653e194be2cb6732ea44587edaa95e",
        "device_model": "HP ENVY x360 2-in-1 Laptop 15-ew0xxx (HP)",
        "device_name": "JUANCARLOS",
        "device_os": "Windows 11  (10.0.22621) 64bit",
    },
    "7929acd96a40fa8c7b34b6f239000fcbf9ec916d": {
        "device_id": "7929acd96a40fa8c7b34b6f239000fcbf9ec916d",
        "device_model": "System Product Name (ASUS)",
        "device_name": "DESKTOP-QN6LRVD",
        "device_os": "Windows 11  (10.0.22000) 64bit",
    },
    "868bea1f78a2b4aa21cbc5b8db94862a": {
        "device_id": "868bea1f78a2b4aa21cbc5b8db94862a",
        "device_model": "samsung SM-A145M",
        "device_name": "Galaxy A14",
        "device_os": "Android OS 13 / API-33 (TP1A.220624.014/A145MUBU2AWF5)",
    },
    "51dd07118cc1cd0b6bac06b9b51703bcfd74c63a": {
        "device_id": "51dd07118cc1cd0b6bac06b9b51703bcfd74c63a",
        "device_model": "System Product Name (ASUS)",
        "device_name": "DESKTOP-QN6LRVD",
        "device_os": "Windows 11  (10.0.22621) 64bit",
    },
    "a6e43cde6c9fda02cc776870c49bac60a727ce59": {
        "device_id": "a6e43cde6c9fda02cc776870c49bac60a727ce59",
        "device_model": "Inspiron 3583 (Dell Inc.)",
        "device_name": "DESKTOP-GFKK43B",
        "device_os": "Windows 11  (10.0.22621) 64bit",
    },
    "ffaa073c10207f34812f6102fee1b020804eec1c": {
        "device_id": "ffaa073c10207f34812f6102fee1b020804eec1c",
        "device_model": "Inspiron 7559 (Dell Inc.)",
        "device_name": "DESKTOP-BNTB2OP",
        "device_os": "Windows 10  (10.0.19045) 64bit",
    },
}


class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def update_lambda_contants(self, prefix, post={}):
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

        if "web-data" in prefix:
            lambda_constants["table_web_data"] = f"web-data"
            lambda_constants["table_project"] = f"web-data"

    def get_region(self):
        if os.environ.get("AWS_EXECUTION_ENV") is None:
            with open(".vscode/enviroment_variables.json", "r", encoding="utf-8") as read_file:
                env_var = json.load(read_file)
                return env_var["region"]
        else:
            import boto3

            session = boto3.session.Session()
            return session.region_name
