import requests
import json

domain_url = "https://cloudviewer.tqs.com.br/"
model_filename_external = "test_project_no_user.zip"
file_path = "tools_for_devs/test_project.zip"
customer_id = "134791"
partner_token = "5SwNgexbWSNmMFFvWo1Dk8bZJSXpC6CdSWF4r8HbcMgBC"

with open(file_path, "rb") as file:
    file_content = file.read()


def start_model_process(model_id, model_upload_path):
    response = requests.request("POST", domain_url + "api/tqs_files_uploaded", headers={}, data=json.dumps({"customer_id": customer_id, "partner_token": partner_token, "model_id": model_id, "model_upload_path": model_upload_path}))
    response = json.loads(response.text)
    if "success" in response:
        print("Success: " + str(response["success"]))
        return response["success"]
    print("Error while calling tqs_files_uploaded: " + response["error"])


def get_tqs_new_model(model_filename_external):
    response = requests.request("POST", domain_url + "api/tqs_new_model", headers={}, data=json.dumps({"customer_id": customer_id, "partner_token": partner_token, "model_filename_external": model_filename_external}))
    response = json.loads(response.text)
    if "success" in response:
        print("Success: " + str(response["success"]))
        return response["success"]
    print("Error while calling tqs_new_model: " + response["error"])


def upload_file_to_aws(aws_keys, file_content):
    data = {"key": aws_keys["key"], "AWSAccessKeyId": aws_keys["AWSAccessKeyId"], "policy": aws_keys["policy"], "signature": aws_keys["signature"], "file": ("filename", file_content, "application/zip")}
    response = requests.post(aws_keys["url"], files=data)
    if response.status_code == 204:
        print("Upload realizado com sucesso")
    else:
        print("Não foi possível realizar o upload")


aws_keys = get_tqs_new_model(model_filename_external)
upload_file_to_aws(aws_keys, file_content)
start_model_process(aws_keys["model_id"], aws_keys["model_upload_path"])

print("END")
