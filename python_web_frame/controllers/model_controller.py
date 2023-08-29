import os

from objects.Model import Model
from utils.Config import lambda_constants
from utils.AWS.S3 import S3
from utils.AWS.Sqs import Sqs
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Lambda import Lambda
from utils.utils.Generate import Generate
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Validation import Validation
from utils.utils.StrFormat import StrFormat
from utils.utils.Http import Http


class ModelController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModelController, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def generate_new_model(self, email, filename=""):
        import datetime

        model_id = Dynamo().get_next_model_id()
        new_model = Model(email, model_id, model_id, "not_created").__dict__
        new_model["model_upload_path"] = datetime.datetime.fromtimestamp(int(float(new_model["created_at"]))).strftime("%Y/%m/%d") + "/" + model_id + "/"
        if filename:
            new_model["model_filename"] = filename
        Dynamo().put_entity(new_model)
        return new_model

    def check_if_file_uploaded_is_valid(self, uploaded_file):
        if not uploaded_file:
            return {"error": "no uploaded_file"}

        ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])

        if not S3().check_if_file_exists(lambda_constants["upload_bucket"], uploaded_file):
            return {"error": "Este model não foi enviado/transferido para a AWS."}

        S3().download_file(lambda_constants["upload_bucket"], uploaded_file, lambda_constants["tmp_path"] + "original_file")

        ifc_location = None
        if self.is_zip_using_magic_number(lambda_constants["tmp_path"] + "original_file"):
            self.extract_zip_file(lambda_constants["tmp_path"] + "original_file", lambda_constants["tmp_path"] + "unzip")
            ifc_location = self.find_file_with_extension_in_directory(lambda_constants["tmp_path"] + "unzip", "ifc")
            if self.is_zip_using_magic_number(ifc_location):
                self.extract_zip_file(ifc_location, lambda_constants["tmp_path"] + "unzipunzip")
                ifc_location = self.find_file_with_extension_in_directory(lambda_constants["tmp_path"] + "unzipunzip", "ifc")
        else:
            ifc_location = lambda_constants["tmp_path"] + "original_file"

        response = {}
        if self.is_ifc_file(ifc_location):
            response["file_format"] = "ifc"
        elif self.is_fbx_file(ifc_location):
            response["file_format"] = "fbx"
        else:
            return {"error": "Nenhum arquivo IFC ou FBX encontrado."}

        new_ifc_location = ifc_location + "." + response["file_format"]
        os.rename(ifc_location, new_ifc_location)
        ifc_location = new_ifc_location

        model = Dynamo().get_model_by_id(self.get_model_id_from_uploaded_file(uploaded_file))

        self.zip_file(ifc_location, lambda_constants["tmp_path"] + "file_ok.zip")

        model["model_filename_zip"] = Generate().generate_short_id() + ".zip"
        model["model_upload_path_zip"] = model["model_upload_path"] + model["model_filename_zip"]

        S3().upload_file(lambda_constants["processed_bucket"], model["model_upload_path_zip"], lambda_constants["tmp_path"] + "file_ok.zip")
        Generate().generate_qr_code(model["model_share_link"], lambda_constants["processed_bucket"], model["model_upload_path_zip"].replace(".zip", ".png"))

        model["model_filesize_ifc"] = str(os.path.getsize(ifc_location))
        model["model_filesize_zip"] = str(os.path.getsize(lambda_constants["tmp_path"] + "file_ok.zip"))
        model["model_share_link"] = lambda_constants["domain_name_url"] + "/webview/?model_id=" + model["model_id"]
        model["model_upload_path_xml"] = model["model_upload_path_zip"].replace(".zip", "-xml.zip")
        model["model_upload_path_aug"] = model["model_upload_path_zip"].replace(".zip", "-aug.zip")
        model["model_upload_path_sd_aug"] = model["model_upload_path_zip"].replace(".zip", "-aug-sd.zip")
        model["model_share_link_qrcode"] = lambda_constants["processed_bucket_cdn"] + "/" + model["model_upload_path_zip"].replace(".zip", ".png")

        response["model"] = model
        return response

    def process_model_file_uploaded(self, model, file_format):
        if not S3().check_if_file_exists(lambda_constants["processed_bucket"], model["model_upload_path_zip"]):
            return {"error": "Este model não foi enviado/transferido para a AWS."}

        if not Validation().check_if_local_env():
            Dynamo().delete_entity(model)

        if file_format == "ifc":
            model = self.change_model_status(model, "not_created", "in_processing")
            model_filesize_ifc_in_megabytes = StrFormat().format_bytes_to_megabytes(model["model_filesize_ifc"])
            ec_requested_gbs = self.generate_ec_requested_gbs(model_filesize_ifc_in_megabytes)
            ec_gbs_bracket = self.generate_ec_gbs_bracket(ec_requested_gbs)
            payloads = self.generate_stepfunctions_payloads(ec_requested_gbs, model)
            ec_gbs_attribute = self.generate_ec_gbs_attribute(ec_requested_gbs)
            ec_message_attribute = {ec_gbs_attribute: {"DataType": "String", "StringValue": ec_gbs_attribute}}

            # ec2_instances = Dynamo().get_ec2_instances()
            # choose_ec2_instance = ec2_instances["ec2_instances"][0]
            # if float(ec_requested_gbs) < 0.0001:
            if float(ec_requested_gbs) < 8:
                model["model_was_processed_where"] = "lambda10gb"
                for payload in payloads:
                    Lambda().start_stepfunction_execution(lambda_constants["stepfunction_arn"], payload)

            # elif float(ec_requested_gbs) < 0.0001:
            elif float(ec_requested_gbs) < 12:
                model["model_was_processed_where"] = "ec2-lambda10gb"
                for payload in payloads:
                    if ".xml" in payload["output_key"]:
                        Lambda().start_stepfunction_execution(lambda_constants["stepfunction_arn"], payload)
                    else:
                        Sqs().send_message(lambda_constants["sqs_queue_url_process_in_ec2"], payload, ec_message_attribute)
                        Lambda().invoke("EC2-Launcher", "Event", {"ec_requested_gbs": ec_gbs_bracket})
                        # Lambda().invoke("EC2-Launcher", "Event", {"ec_requested_gbs": ec_gbs_bracket, "ec2_instance": choose_ec2_instance})

            else:
                model["model_was_processed_where"] = "ec2"
                for payload in payloads:
                    Sqs().send_message(lambda_constants["sqs_queue_url_process_in_ec2"], payload, ec_message_attribute)
                    Lambda().invoke("EC2-Launcher", "Event", {"ec_requested_gbs": ec_gbs_bracket})
                    # Lambda().invoke("EC2-Launcher", "Event", {"ec_requested_gbs": ec_gbs_bracket, "ec2_instance": choose_ec2_instance})

            # ec2_instances["ec2_instances"].remove(choose_ec2_instance)
            # Dynamo().put_entity(ec2_instances)
            Dynamo().put_entity(model)
            data = {"model_id": model["model_id"], "output_format": "process_started"}
            Http().request("POST", "https://" + lambda_constants["prefix_name"] + lambda_constants["domain_name"] + lambda_constants["sufix_name"] + "/api/update_model_process", headers={}, data=data)
            return {"success": "Model " + model["model_id"] + " agora em processamento."}

    def generate_stepfunctions_payloads(self, ec_requested_gbs, model):
        from utils.Config import lambda_constants

        return [
            {"ec_requested_gbs": ec_requested_gbs, "model_id": model["model_id"], "input_bucket": lambda_constants["processed_bucket"], "input_key": model["model_upload_path_zip"], "output_bucket": lambda_constants["processed_bucket"], "output_key": model["model_upload_path_zip"].replace(".zip", ".xml"), "output_project_domain_name": lambda_constants["prefix_name"] + lambda_constants["domain_name"] + lambda_constants["sufix_name"]},
            {"ec_requested_gbs": ec_requested_gbs, "model_id": model["model_id"], "input_bucket": lambda_constants["processed_bucket"], "input_key": model["model_upload_path_zip"], "output_bucket": lambda_constants["processed_bucket"], "output_key": model["model_upload_path_zip"].replace(".zip", ".aug"), "output_project_domain_name": lambda_constants["prefix_name"] + lambda_constants["domain_name"] + lambda_constants["sufix_name"]},
            {"ec_requested_gbs": ec_requested_gbs, "model_id": model["model_id"], "input_bucket": lambda_constants["processed_bucket"], "input_key": model["model_upload_path_zip"], "output_bucket": lambda_constants["processed_bucket"], "output_key": model["model_upload_path_zip"].replace(".zip", ".aug"), "output_project_domain_name": lambda_constants["prefix_name"] + lambda_constants["domain_name"] + lambda_constants["sufix_name"], "output_simplify": "true"},
        ]

    def calculate_model_process_percentage(self, model):
        total_percentage = 0

        if model.get("model_processing_started"):
            total_percentage += 2
        if model.get("model_xml_started"):
            total_percentage += 2
        if model.get("model_aug_started"):
            total_percentage += 2
        if model.get("model_aug_sd_started"):
            total_percentage += 2
        if model.get("model_xml_to_dynamo_start"):
            total_percentage += 2
        if model.get("model_xml_to_dynamo_completed"):
            total_percentage += 15
        if model.get("model_xml_completed"):
            total_percentage += 15
        if model.get("model_aug_completed"):
            total_percentage += 30
        else:
            total_percentage += int(model["model_aug_percent"]) * 0.20
        if model.get("model_aug_sd_completed"):
            total_percentage += 30
        else:
            total_percentage += int(model["model_aug_sd_percent"]) * 0.20
        return str(total_percentage)

    def calculate_model_total_time(self, model):
        model["model_xml_to_dynamo_total_time"] = str(float(model["model_xml_to_dynamo_completed"]) - float(model["model_xml_to_dynamo_start"]))
        model["model_xml_total_time"] = str(float(model["model_xml_completed"]) - float(model["model_xml_started"]))
        model["model_aug_total_time"] = str(float(model["model_aug_completed"]) - float(model["model_aug_started"]))
        model["model_aug_sd_total_time"] = str(float(model["model_aug_sd_completed"]) - float(model["model_aug_sd_started"]))
        model["model_processing_total_time"] = str(float(model["model_xml_to_dynamo_total_time"]) + float(model["model_xml_total_time"]) + float(model["model_aug_total_time"]) + float(model["model_aug_sd_total_time"]))
        return model

    def calculate_model_memory_usage_in_gbs(self, model):
        if not "model_memory_usage_in_gbs" in model:
            model["model_memory_usage_in_gbs"] = "0.0"
        if not "model_xml_memory_usage" in model:
            model["model_xml_memory_usage"] = "0.0"
        if not "model_aug_memory_usage" in model:
            model["model_aug_memory_usage"] = "0.0"
        if not "model_aug_sd_memory_usage" in model:
            model["model_aug_sd_memory_usage"] = "0.0"

        model_memory_usages = [model["model_xml_memory_usage"], model["model_aug_memory_usage"], model["model_aug_sd_memory_usage"]]
        for memory_usage in model_memory_usages:
            if float(memory_usage) > float(model["model_memory_usage_in_gbs"]):
                model["model_memory_usage_in_gbs"] = memory_usage

        return model

    def change_model_status(self, model, current_status, next_status):
        model["pk"] = model["pk"].replace(current_status, next_status)
        model["model_state"] = model["model_state"].replace(current_status, next_status)
        return model

    def generate_ec_requested_gbs(self, model_filesize_ifc_in_megabytes):
        mbs_converted = model_filesize_ifc_in_megabytes / 25
        return str(mbs_converted)

    def generate_ec_gbs_attribute(self, ec_requested_gbs):
        ec_gbs_attribute = "16gbs"
        if float(ec_requested_gbs) > 14 and float(ec_requested_gbs) <= 30:
            ec_gbs_attribute = "32gbs"
        elif float(ec_requested_gbs) > 30 and float(ec_requested_gbs) <= 60:
            ec_gbs_attribute = "62gbs"
        elif float(ec_requested_gbs) > 60:
            ec_gbs_attribute = "128gbs"
        return ec_gbs_attribute

    def generate_ec_gbs_bracket(self, ec_requested_gbs):
        ec_gbs_bracket = "16.0"
        if float(ec_requested_gbs) > 14 and float(ec_requested_gbs) < 30:
            ec_gbs_bracket = "32.0"
        if float(ec_requested_gbs) > 30 and float(ec_requested_gbs) < 60:
            ec_gbs_bracket = "62.0"
        if float(ec_requested_gbs) > 60:
            ec_gbs_bracket = "128.0"
        return ec_gbs_bracket

    def get_model_id_from_uploaded_file(self, uploaded_file):
        return uploaded_file.split("/")[-2]

    def extract_zip_file(self, zip_file_path, extract_path):
        import zipfile

        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

    def zip_file(self, file_to_be_ziped_location, zip_destiny_location):
        import zipfile

        with zipfile.ZipFile(zip_destiny_location, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as myzip:
            myzip.write(file_to_be_ziped_location, arcname=os.path.basename(file_to_be_ziped_location))
            print("Zip Generated " + zip_destiny_location)

    def is_ifc_file(self, file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
            return first_line in ["ISO-10303-21", "ISO-10303-21;"]

    def is_fbx_file(self, file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
            return first_line in ["ISO-10303-21", "ISO-10303-21;"]

    def is_zip_using_magic_number(self, filename):
        with open(filename, "rb") as f:
            magic_number = f.read(4)
        return magic_number in [b"\x50\x4B\x03\x04", b"\x50\x4B\x05\x06", b"\x50\x4B\x07\x08"]

    def find_file_with_extension_in_directory(self, root_directory, extension):
        import os

        for root, dirs, files in os.walk(root_directory):
            for file in files:
                if file.lower().endswith("." + extension.lower()):
                    return os.path.join(root, file).replace("\\", "/")

        return None

    def check_if_model_in_processing_is_with_error(self, model_created_at):
        import time

        if (int(time.time()) - int(float(model_created_at))) > 28800:
            return True
        return False
