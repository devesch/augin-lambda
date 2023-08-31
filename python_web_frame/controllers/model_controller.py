import os
from objects.Model import Model
from utils.Config import lambda_constants
from utils.AWS.S3 import S3
from utils.AWS.Sqs import Sqs
from utils.AWS.Ses import Ses
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Lambda import Lambda
from utils.utils.Generate import Generate
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Validation import Validation
from utils.utils.StrFormat import StrFormat
from utils.utils.Http import Http
from utils.utils.Sort import Sort


class ModelController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModelController, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def generate_bin_files(self, model, output_bucket, output_key):
        xml_zip_location = lambda_constants["tmp_path"] + "model_xml.zip"
        unzip_location = lambda_constants["tmp_path"] + "model/"
        bin_location = lambda_constants["tmp_path"] + "model_bin.bin"
        mini_bin_location = lambda_constants["tmp_path"] + "mini_model_bin.bin"
        bin_zip_location = lambda_constants["tmp_path"] + "model_bin.zip"
        mini_bin_zip_location = lambda_constants["tmp_path"] + "model_mini_bin.zip"
        bin_model_key = output_key.replace("-xml.zip", "-bin.zip")
        mini_bin_model_key = output_key.replace("-xml.zip", "-mini-bin.zip")

        ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])

        S3().download_file(output_bucket, output_key, xml_zip_location)
        ReadWrite().extract_zip_file(xml_zip_location, unzip_location)
        xml_location = self.find_file_with_extension_in_directory(unzip_location, ["xml"])

        import xml_binary
        import importlib
        import time

        importlib.reload(xml_binary)

        xml_binary.run_xml_binary(xml_location, bin_location)
        time.sleep(1)
        if not os.path.exists(bin_location):
            raise Exception("Unable to generate bin files")
        else:
            ReadWrite().zip_file(bin_location, bin_zip_location)
            S3().upload_file(output_bucket, bin_model_key, bin_zip_location)

            ReadWrite().zip_file(mini_bin_location, mini_bin_zip_location)
            S3().upload_file(output_bucket, mini_bin_model_key, mini_bin_zip_location)

            Dynamo().update_entity(model, "model_upload_path_bin", bin_model_key)
            Dynamo().update_entity(model, "model_upload_path_mini_bin", mini_bin_model_key)

    def sort_models(self, models, sort_attribute="model_filename", sort_reverse=False):
        sort_reverse = sort_reverse == "True"
        favorited_models = []
        normal_models = []
        sorted_models = []
        if models:
            for model in models:
                if model.get("model_is_favorite"):
                    favorited_models.append(model)
                else:
                    normal_models.append(model)

        if sort_attribute == "model_filename":
            favorited_models = Sort().sort_dict_list(favorited_models, sort_attribute, reverse=sort_reverse, integer=False)
            normal_models = Sort().sort_dict_list(normal_models, sort_attribute, reverse=sort_reverse, integer=False)
        else:
            favorited_models = Sort().sort_dict_list(favorited_models, sort_attribute, reverse=sort_reverse, integer=True)
            normal_models = Sort().sort_dict_list(normal_models, sort_attribute, reverse=sort_reverse, integer=True)

        sorted_models.extend(favorited_models)
        sorted_models.extend(normal_models)
        return sorted_models

    def check_if_model_is_too_big(self, model_filesize_ifc):
        return int(model_filesize_ifc) > 1073741824  ### 1gb

    def convert_model_filesize_ifc_to_mb(self, model_filesize_ifc):
        return str(round(int(model_filesize_ifc) / 1024 / 1024, 1))

    def convert_model_created_at_to_date(self, created_at):
        from datetime import datetime

        # Create a datetime object from the Unix timestamp
        dt_object = datetime.fromtimestamp(float(created_at))
        formatted_date = dt_object.strftime("%b %d, %Y")
        return formatted_date

    def delete_model(self, model):
        S3().delete_folder(lambda_constants["processed_bucket"], model["model_upload_path"])
        Dynamo().delete_entity(model)

    def generate_new_model(self, email, filename=""):
        import datetime

        model_id = Dynamo().get_next_model_id()
        new_model = Model(email, model_id, model_id, "not_created").__dict__
        new_model["model_upload_path"] = datetime.datetime.fromtimestamp(int(float(new_model["created_at"]))).strftime("%Y/%m/%d") + "/" + model_id + "/"
        if filename:
            new_model["model_filename"] = filename
        Dynamo().put_entity(new_model)
        return new_model

    def check_if_file_uploaded_is_valid(self, uploaded_file, user):
        if not uploaded_file:
            return {"error": "no uploaded_file"}

        ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])

        if not S3().check_if_file_exists(lambda_constants["upload_bucket"], uploaded_file):
            return {"error": "Este model não foi enviado/transferido para a AWS."}

        S3().download_file(lambda_constants["upload_bucket"], uploaded_file, lambda_constants["tmp_path"] + "original_file")

        ifc_location = None
        ifcs_locations = []
        if self.is_zip_using_magic_number(lambda_constants["tmp_path"] + "original_file"):
            ReadWrite().extract_zip_file(lambda_constants["tmp_path"] + "original_file", lambda_constants["tmp_path"] + "unzip")
            ifc_location = self.find_file_with_extension_in_directory(lambda_constants["tmp_path"] + "unzip", ["ifc", "fbx"])
            if not ifc_location:
                return {"error": "Nenhum arquivo IFC ou FBX encontrado."}
            if self.is_zip_using_magic_number(ifc_location):
                ReadWrite().extract_zip_file(ifc_location, lambda_constants["tmp_path"] + "unzipunzip")
                ifcs_locations = self.find_all_files_with_extension_in_directory(lambda_constants["tmp_path"] + "unzipunzip", ["ifc", "fbx"])
            else:
                ifcs_locations = self.find_all_files_with_extension_in_directory(lambda_constants["tmp_path"] + "unzip", ["ifc", "fbx"])
        else:
            ifc_location = lambda_constants["tmp_path"] + "original_file"
            ifcs_locations = [ifc_location]

        response = {"models_ids": []}

        for index, ifc_location in enumerate(ifcs_locations):
            if os.path.getsize(ifc_location) > int(lambda_constants["maxium_ifc_project_filesize"]):
                return {"error": "O projeto excede o tamanho máximo de 1Gb."}
            if not self.is_ifc_file(ifc_location) and not self.is_fbx_file(ifc_location):
                return {"error": "Nenhum arquivo IFC ou FBX encontrado."}
            if self.is_ifc_file(ifc_location):
                if not self.is_acceptable_ifc_format(ifc_location):
                    return {"error": "Os formartos suportados de IFC são: IFC2x3 e IFC4."}

        if len(ifcs_locations) > 1:
            response["has_more_than_one_file"] = True
        else:
            response["has_more_than_one_file"] = False

        for index, ifc_location in enumerate(ifcs_locations):
            if self.is_ifc_file(ifc_location):
                file_format = "ifc"
            elif self.is_fbx_file(ifc_location):
                file_format = "fbx"

            if not "." + file_format in ifc_location:
                new_ifc_location = ifc_location + "." + file_format
                os.rename(ifc_location, new_ifc_location)
                ifc_location = new_ifc_location

            if index == 0:
                model = Dynamo().get_model_by_id(self.get_model_id_from_uploaded_file(uploaded_file))
            else:
                model = self.generate_new_model(user.user_email, os.path.basename(ifc_location))

            ReadWrite().zip_file(ifc_location, lambda_constants["tmp_path"] + "file_ok.zip")

            model["model_filename_zip"] = Generate().generate_short_id() + ".zip"
            model["model_upload_path_zip"] = model["model_upload_path"] + model["model_filename_zip"]

            S3().upload_file(lambda_constants["processed_bucket"], model["model_upload_path_zip"], lambda_constants["tmp_path"] + "file_ok.zip")
            Generate().generate_qr_code(model["model_share_link"], lambda_constants["processed_bucket"], model["model_upload_path_zip"].replace(".zip", ".png"))

            model["model_format"] = file_format
            model["model_filesize_ifc"] = str(os.path.getsize(ifc_location))
            model["model_filesize_zip"] = str(os.path.getsize(lambda_constants["tmp_path"] + "file_ok.zip"))
            model["model_share_link"] = lambda_constants["domain_name_url"] + "/webview/?model_id=" + model["model_id"]
            model["model_upload_path_xml"] = model["model_upload_path_zip"].replace(".zip", "-xml.zip")
            model["model_upload_path_aug"] = model["model_upload_path_zip"].replace(".zip", "-aug.zip")
            model["model_upload_path_sd_aug"] = model["model_upload_path_zip"].replace(".zip", "-aug-sd.zip")
            model["model_share_link_qrcode"] = lambda_constants["processed_bucket_cdn"] + "/" + model["model_upload_path_zip"].replace(".zip", ".png")

            response["models_ids"].append(model["model_id"])
            Dynamo().put_entity(model)
        return response

    def process_model_file_uploaded(self, model):
        if not S3().check_if_file_exists(lambda_constants["processed_bucket"], model["model_upload_path_zip"]):
            return {"error": "Este model não foi enviado/transferido para a AWS."}

        if not Validation().check_if_local_env():
            Dynamo().delete_entity(model)

        if model["model_format"] == "ifc":
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
            model["model_processing_started"] = True
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

    def is_ifc_file(self, file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
            return first_line in ["ISO-10303-21", "ISO-10303-21;"]

    def is_acceptable_ifc_format(self, file_path):
        acceptable_versions = ["IFC2X3", "IFC4"]

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "FILE_SCHEMA" in line.upper():
                    version_info = line.upper().split("'")
                    if len(version_info) > 1:
                        version = version_info[1]
                        return version in acceptable_versions

        return False

    def is_fbx_file(self, file_path):
        try:
            with open(file_path, "rb") as f:  # Read as binary
                header = f.read(20)  # Read first 20 bytes
                return b"Kaydara FBX Binary" in header
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def is_zip_using_magic_number(self, filename):
        with open(filename, "rb") as f:
            magic_number = f.read(4)
        return magic_number in [b"\x50\x4B\x03\x04", b"\x50\x4B\x05\x06", b"\x50\x4B\x07\x08"]

    def find_file_with_extension_in_directory(self, root_directory, extensions):
        import os

        for root, dirs, files in os.walk(root_directory):
            for file in files:
                for extension in extensions:
                    if file.lower().endswith("." + extension.lower()):
                        return os.path.join(root, file).replace("\\", "/")

        return None

    def find_all_files_with_extension_in_directory(self, root_directory, extensions):
        import os

        files_with_extension = []

        for root, dirs, files in os.walk(root_directory):
            for file in files:
                for extension in extensions:
                    if file.lower().endswith("." + extension.lower()):
                        files_with_extension.append(os.path.join(root, file).replace("\\", "/"))

        return files_with_extension

    def check_if_model_in_processing_is_with_error(self, model_created_at):
        import time

        if (int(time.time()) - int(float(model_created_at))) > 28800:
            return True
        return False
