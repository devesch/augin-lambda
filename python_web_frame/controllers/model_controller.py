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

    def remove_model_id_from_federated_model(self, federated_model, model_id_to_be_removed):
        model_to_be_removed = Dynamo().get_model(model_id_to_be_removed)
        if model_to_be_removed and model_to_be_removed.get("model_used_in_federated_ids") and federated_model["model_id"] in model_to_be_removed["model_used_in_federated_ids"]:
            model_to_be_removed["model_used_in_federated_ids"].remove(federated_model["model_id"])
            Dynamo().put_entity(model_to_be_removed)

        if model_id_to_be_removed in federated_model["model_federated_required_ids"]:
            federated_model["model_federated_required_ids"].remove(model_id_to_be_removed)

            federated_model_filesize = 0
            federated_required_models = Dynamo().batch_get_models(federated_model["model_federated_required_ids"])
            if federated_required_models:
                for required_model in federated_required_models:
                    federated_model_filesize += int(required_model["model_filesize"])

            federated_model["model_filesize"] = str(federated_model_filesize)

        Dynamo().put_entity(federated_model)

    def update_federated_required_models(self, federated_model, federated_required_models):
        federated_model_required_ids = []
        federated_model_filesize = 0

        for required_model in federated_required_models:
            federated_model_required_ids.append(required_model["model_id"])
            if federated_model["model_id"] not in required_model["model_used_in_federated_ids"]:
                required_model["model_used_in_federated_ids"].append(federated_model["model_id"])
                Dynamo().put_entity(required_model)
            federated_model_filesize += int(required_model["model_filesize"])

        federated_model["model_federated_required_ids"] = federated_model_required_ids
        federated_model["model_filesize"] = str(federated_model_filesize)
        Dynamo().put_entity(federated_model)

    def get_already_uploaded_models(self, user):
        already_uploaded_models = []
        not_created_models = Dynamo().query_user_models_from_state(user, "not_created")
        if not_created_models:
            for model in not_created_models:
                if not model["model_share_link_qrcode"]:
                    self.delete_model(model, user)
                else:
                    already_uploaded_models.append(model)
        return already_uploaded_models

    def search_models_by_name(self, search_input, user, shared=False):
        matching_name_models = []
        if shared:
            user_shared_dicts = Dynamo().get_folder(user.user_shared_dicts_folder_id)
            for folder_id in user_shared_dicts["folders"]:
                folder = Dynamo().get_folder(folder_id)
                if folder:
                    matching_name_models = self.add_folder_files_to_matching_name_models(search_input, folder["files"], matching_name_models)
            matching_name_models = self.add_folder_files_to_matching_name_models(search_input, user_shared_dicts["files"], matching_name_models)

        else:
            completed_models = Dynamo().query_user_models_from_state(user, "completed")
            if completed_models:
                for model in completed_models:
                    if search_input.lower() in model["model_name"].lower():
                        matching_name_models.append(model)
        return matching_name_models

    def add_folder_files_to_matching_name_models(self, search_input, folder_files, matching_name_models):
        if folder_files:
            for model_id in folder_files:
                model = Dynamo().get_model(model_id)
                if model:
                    if search_input.lower() in model["model_name"].lower():
                        matching_name_models.append(model)
        return matching_name_models

    def publish_federated_model(self, federated_model_id):
        model = Dynamo().get_model(federated_model_id)
        model["model_filesize"] = "0"
        for model_id in model["model_federated_required_ids"]:
            required_model = Dynamo().get_model(model_id)
            if required_model["model_state"] != "completed":
                return False
            model["model_filesize"] = str(int(model["model_filesize"]) + int(required_model["model_filesize"]))
        model["model_upload_path_zip"] = (model["model_upload_path"]) + model["model_name"] + ".zip"
        model["model_share_link"] = lambda_constants["domain_name_url"] + "/webview/?model_code=" + model["model_code"]
        model["model_share_link_qrcode"] = lambda_constants["processed_bucket_cdn"] + "/" + model["model_upload_path_zip"].replace(".zip", ".png")
        Generate().generate_qr_code(model["model_share_link"], lambda_constants["processed_bucket"], model["model_upload_path_zip"].replace(".zip", ".png"))

        model = self.change_model_state(model, "not_created", "completed")
        Dynamo().put_entity(model)
        return model

    def generate_model_download_link(self, model):
        return lambda_constants["processed_bucket_cdn"] + "/" + model["model_upload_path_zip"]

    def update_model_files(self, destination_model, source_model, user):
        if source_model["model_format"] == "ifc":
            destination_model["model_project_id"] = source_model["model_project_id"]
            destination_model["model_filename"] = source_model["model_filename"]
            destination_model["model_filename_zip"] = source_model["model_filename_zip"]

            destination_model["model_upload_path_zip"] = source_model["model_upload_path_zip"].replace(source_model["model_upload_path"], destination_model["model_upload_path"])
            destination_model["model_upload_path_xml"] = source_model["model_upload_path_xml"].replace(source_model["model_upload_path"], destination_model["model_upload_path"])
            destination_model["model_upload_path_aug"] = source_model["model_upload_path_aug"].replace(source_model["model_upload_path"], destination_model["model_upload_path"])
            destination_model["model_upload_path_sd_aug"] = source_model["model_upload_path_sd_aug"].replace(source_model["model_upload_path"], destination_model["model_upload_path"])
            destination_model["model_upload_path_bin"] = source_model["model_upload_path_bin"].replace(source_model["model_upload_path"], destination_model["model_upload_path"])
            destination_model["model_upload_path_mini_bin"] = source_model["model_upload_path_mini_bin"].replace(source_model["model_upload_path"], destination_model["model_upload_path"])

            S3().copy_file_in_bucket(lambda_constants["processed_bucket"], source_model["model_upload_path_zip"], destination_model["model_upload_path_zip"])
            S3().copy_file_in_bucket(lambda_constants["processed_bucket"], source_model["model_upload_path_xml"], destination_model["model_upload_path_xml"])
            S3().copy_file_in_bucket(lambda_constants["processed_bucket"], source_model["model_upload_path_aug"], destination_model["model_upload_path_aug"])
            S3().copy_file_in_bucket(lambda_constants["processed_bucket"], source_model["model_upload_path_sd_aug"], destination_model["model_upload_path_sd_aug"])
            S3().copy_file_in_bucket(lambda_constants["processed_bucket"], source_model["model_upload_path_bin"], destination_model["model_upload_path_bin"])
            S3().copy_file_in_bucket(lambda_constants["processed_bucket"], source_model["model_upload_path_mini_bin"], destination_model["model_upload_path_mini_bin"])

            destination_model["model_filesize"] = source_model["model_filesize"]
            destination_model["model_filesize_zip"] = source_model["model_filesize_zip"]
            destination_model["model_filesize_xml"] = source_model["model_filesize_xml"]
            destination_model["model_filesize_aug"] = source_model["model_filesize_aug"]
            destination_model["model_filesize_sd_aug"] = source_model["model_filesize_sd_aug"]
            destination_model["model_filesize_bin"] = source_model["model_filesize_bin"]
            destination_model["model_filesize_mini_bin"] = source_model["model_filesize_mini_bin"]

            destination_model["model_memory_usage_in_gbs"] = str(source_model.get("model_memory_usage_in_gbs"))
            destination_model["model_was_processed_where"] = str(source_model.get("model_was_processed_where"))
            destination_model["model_xml_started"] = str(source_model.get("model_xml_started"))
            destination_model["model_xml_memory_usage"] = str(source_model.get("model_xml_memory_usage"))
            destination_model["model_xml_completed"] = str(source_model.get("model_xml_completed"))
            destination_model["model_xml_total_time"] = str(source_model.get("model_xml_total_time"))
            destination_model["model_xml_to_dynamo_start"] = str(source_model.get("model_xml_to_dynamo_start"))
            destination_model["model_xml_to_dynamo_completed"] = str(source_model.get("model_xml_to_dynamo_completed"))
            destination_model["model_xml_to_dynamo_total_time"] = str(source_model.get("model_xml_to_dynamo_total_time"))
            destination_model["model_aug_started"] = str(source_model.get("model_aug_started"))
            destination_model["model_aug_percent"] = str(source_model.get("model_aug_percent"))
            destination_model["model_aug_memory_usage"] = str(source_model.get("model_aug_memory_usage"))
            destination_model["model_aug_completed"] = str(source_model.get("model_aug_completed"))
            destination_model["model_aug_total_time"] = str(source_model.get("model_aug_total_time"))
            destination_model["model_aug_sd_started"] = str(source_model.get("model_aug_sd_started"))
            destination_model["model_aug_sd_percent"] = str(source_model.get("model_aug_sd_percent"))
            destination_model["model_aug_sd_memory_usage"] = str(source_model.get("model_aug_sd_memory_usage"))
            destination_model["model_aug_sd_completed"] = str(source_model.get("model_aug_sd_completed"))
            destination_model["model_aug_sd_total_time"] = str(source_model.get("model_aug_sd_total_time"))
            destination_model["model_processing_total_time"] = str(source_model.get("model_processing_total_time"))
            destination_model["model_processing_percentage"] = str(source_model.get("model_processing_percentage"))
            destination_model["model_valid_until"] = str(source_model.get("model_valid_until"))

        elif source_model["model_format"] in ["fbx", "glb"]:
            destination_model["model_filename"] = source_model["model_filename"]
            destination_model["model_filename_zip"] = source_model["model_filename_zip"]

            destination_model["model_upload_path_zip"] = source_model["model_upload_path_zip"].replace(source_model["model_upload_path"], destination_model["model_upload_path"])
            destination_model["model_upload_path_glb"] = source_model["model_upload_path_glb"].replace(source_model["model_upload_path"], destination_model["model_upload_path"])

            S3().copy_file_in_bucket(lambda_constants["processed_bucket"], source_model["model_upload_path_zip"], destination_model["model_upload_path_zip"])
            S3().copy_file_in_bucket(lambda_constants["processed_bucket"], source_model["model_upload_path_glb"], destination_model["model_upload_path_glb"])

            destination_model["model_filesize"] = source_model["model_filesize"]
            destination_model["model_filesize_glb"] = source_model["model_filesize_glb"]

        Dynamo().put_entity(destination_model)
        self.delete_model(source_model, user)

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
        xml_location = ReadWrite().find_file_with_extension_in_directory(unzip_location, ["xml"])

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

    def sort_models(self, user, models, sort_attribute="model_name", sort_reverse=False):
        sort_reverse = sort_reverse == "True"

        if sort_attribute not in models[0]:
            sort_attribute = "model_name"

        favorited_models = []
        normal_models = []
        sorted_models = []
        if models:
            for model in models:
                if user and model["model_id"] in user.user_favorited_models:
                    favorited_models.append(model)
                else:
                    normal_models.append(model)

        if sort_attribute in ["created_at", "model_filesize"]:
            sort_reverse = not sort_reverse

        if sort_attribute in ["model_name", "owners_name"]:
            favorited_models = Sort().sort_dict_list(favorited_models, sort_attribute, reverse=sort_reverse, integer=False)
            normal_models = Sort().sort_dict_list(normal_models, sort_attribute, reverse=sort_reverse, integer=False)
        else:
            favorited_models = Sort().sort_dict_list(favorited_models, sort_attribute, reverse=sort_reverse, integer=True)
            normal_models = Sort().sort_dict_list(normal_models, sort_attribute, reverse=sort_reverse, integer=True)

        sorted_models.extend(favorited_models)
        sorted_models.extend(normal_models)
        return sorted_models

    def check_if_model_is_too_big(self, model_filesize):
        return int(model_filesize) > 1073741824  ### 1gb

    def convert_model_filesize_to_mb(self, model_filesize):
        return str(round(int(model_filesize) / 1024 / 1024, 1))

    def delete_model(self, model, user):
        if model["model_used_in_federated_ids"]:
            for model_id in model["model_used_in_federated_ids"]:
                federated_model = Dynamo().get_model(model_id)
                if model["model_id"] in federated_model["model_federated_required_ids"]:
                    federated_model["model_federated_required_ids"].remove(model["model_id"])
                    Dynamo().put_entity(federated_model)

        if model["model_federated_required_ids"]:
            for model_id in model["model_federated_required_ids"]:
                required_model = Dynamo().get_model(model_id)
                if required_model:
                    if model["model_id"] in required_model["model_used_in_federated_ids"]:
                        required_model["model_used_in_federated_ids"].remove(model["model_id"])
                        Dynamo().put_entity(required_model)
        if model["model_state"] == "completed":
            user.remove_model_from_user_dicts(model)
        Lambda().invoke(lambda_constants["lambda_move_deleted_model_files"], "Event", {"model_upload_path": model["model_upload_path"], "model_state": model["model_state"]})
        model = self.change_model_state(model, model["model_state"], "deleted")
        Dynamo().put_entity(model)

    def generate_new_model(self, user, filename="", federated=False, federated_required_ids=[]):
        import datetime

        model_id = Dynamo().get_next_model_id()
        new_model = Model(user.user_id, model_id, model_id, "not_created", user.user_dicts_folder_id).__dict__
        new_model["model_upload_path"] = datetime.datetime.fromtimestamp(int(float(new_model["created_at"]))).strftime("%Y/%m/%d") + "/" + model_id + "/"

        if filename:
            new_model["model_name"] = filename
            new_model["model_filename"] = filename
        if federated:
            federated_model_already_completed = True
            federated_filesize = 0
            filtered_federated_required_ids = []
            for required_model_id in federated_required_ids:
                required_model = Dynamo().get_model(required_model_id)
                if required_model:
                    if required_model["model_format"] == "ifc":
                        filtered_federated_required_ids.append(required_model_id)
                    if required_model["model_state"] != "completed":
                        federated_model_already_completed = False
                    federated_filesize += int(required_model["model_filesize"])
            new_model["model_is_federated"] = True
            new_model["model_federated_required_ids"] = filtered_federated_required_ids
            new_model["model_category"] = "federated"
            if federated_model_already_completed:
                new_model = self.change_model_state(new_model, "not_created", "completed")
                new_model["model_filesize"] = str(federated_filesize)
                user.add_model_to_user_dicts(new_model)
        Dynamo().put_entity(new_model)
        return new_model

    def check_if_file_uploaded_is_valid(self, uploaded_file, original_name, user):
        if not uploaded_file:
            return {"error": "no uploaded_file"}

        original_name = original_name.replace("/", "").replace("?", "").replace("$", "")

        ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])

        if not S3().check_if_file_exists(lambda_constants["upload_bucket"], uploaded_file):
            return {"error": "Este model não foi enviado/transferido para a AWS."}

        S3().download_file(lambda_constants["upload_bucket"], uploaded_file, lambda_constants["tmp_path"] + original_name)

        ifc_location = None
        ifcs_locations = []
        if self.is_zip_using_magic_number(lambda_constants["tmp_path"] + original_name):
            if Validation().check_if_zip_is_password_protected(lambda_constants["tmp_path"] + original_name):
                return {"error": "O arquivo .zip se encontra trancado com senha."}
            ReadWrite().extract_zip_file(lambda_constants["tmp_path"] + original_name, lambda_constants["tmp_path"] + "unzip")
            ifc_location = ReadWrite().find_file_with_extension_in_directory(lambda_constants["tmp_path"] + "unzip", ["ifc", "fbx"])
            if not ifc_location:
                return {"error": "Nenhum arquivo IFC ou FBX encontrado."}
            if self.is_zip_using_magic_number(ifc_location):
                if Validation().check_if_zip_is_password_protected(ifc_location):
                    return {"error": "O arquivo .zip se encontra trancado com senha."}
                ReadWrite().extract_zip_file(ifc_location, lambda_constants["tmp_path"] + "unzipunzip")
                ifcs_locations = self.find_all_files_with_extension_in_directory(lambda_constants["tmp_path"] + "unzipunzip", ["ifc", "fbx", "glb"])
            else:
                ifcs_locations = self.find_all_files_with_extension_in_directory(lambda_constants["tmp_path"] + "unzip", ["ifc", "fbx", "glb"])
        else:
            ifc_location = lambda_constants["tmp_path"] + original_name
            ifcs_locations = [ifc_location]

        response = {"success": {"models_ids": [], "file_formats": {}, "message": "", "model_already_exists_name": ""}}

        user_plan = user.get_user_actual_plan()
        files_hashes = []
        for index, ifc_location in enumerate(ifcs_locations):

            file_hash = ReadWrite().get_file_hash(ifc_location)
            if file_hash not in files_hashes:
                files_hashes.append(file_hash)
            else:
                return {"error": "O .zip contem arquivos duplicados."}

            if os.path.getsize(ifc_location) > int(lambda_constants["maxium_ifc_project_filesize"]):
                if index == 0:
                    return {"error": "O projeto excede o tamanho máximo de 1Gb."}
                else:
                    return {"error": "Algum arquivo dentro do .zip excede o tamanho máximo de 1Gb."}
            if (os.path.getsize(ifc_location) / (10**6)) > int(user_plan["plan_maxium_model_size_in_mbs"]):
                if index == 0:
                    return {"error": "O projeto excede o tamanho máximo da suportado pela sua conta."}
                else:
                    return {"error": "Algum arquivo dentro do .zip excede o tamanho máximo da suportado pela sua conta."}

            if not self.is_ifc_file(ifc_location) and not self.is_fbx_file(ifc_location) and not self.is_glb_file(ifc_location):
                return {"error": "Algum arquivo dentro do .zip é inválido."}
            if self.is_ifc_file(ifc_location):
                if not self.is_acceptable_ifc_format(ifc_location):
                    if index == 0:
                        return {"error": "Os formartos suportados de IFC são: IFC2x3 e IFC4."}
                    else:
                        return {"error": "Algum arquivo dentro do .zip não está dentro dos nossos formatos suportados: suportados de IFC são: IFC2x3 e IFC4."}

            models_in_processing = Dynamo().query_user_models_from_state(user, "in_processing")
            if models_in_processing:
                for model_in_processing in models_in_processing:
                    if model_in_processing.get("model_filehash") == file_hash:
                        return {"error": "Este mesmo arquivo já se encontra na fila de processamento."}

        if len(ifcs_locations) > 1:
            response["success"]["has_more_than_one_file"] = True
        else:
            response["success"]["has_more_than_one_file"] = False

        response["success"]["has_fbx"] = False
        for index, ifc_location in enumerate(ifcs_locations):
            if self.is_ifc_file(ifc_location):
                file_format = "ifc"

                if "ifc" not in response["success"]["file_formats"]:
                    response["success"]["file_formats"]["ifc"] = 1
                else:
                    response["success"]["file_formats"]["ifc"] += 1

            elif self.is_fbx_file(ifc_location):
                file_format = "fbx"
                response["success"]["has_fbx"] = True

                if "fbx" not in response["success"]["file_formats"]:
                    response["success"]["file_formats"]["fbx"] = 1
                else:
                    response["success"]["file_formats"]["fbx"] += 1

            elif self.is_glb_file(ifc_location):
                file_format = "glb"
                response["success"]["has_fbx"] = True

                if "glb" not in response["success"]["file_formats"]:
                    response["success"]["file_formats"]["glb"] = 1
                else:
                    response["success"]["file_formats"]["glb"] += 1

            if not "." + file_format in ifc_location:
                new_ifc_location = ifc_location + "." + file_format
                os.rename(ifc_location, new_ifc_location)
                ifc_location = new_ifc_location

            models_with_same_filehash = Dynamo().query_models_by_filehash(ReadWrite().get_file_hash(ifc_location))
            model_already_exits = False
            if models_with_same_filehash:
                for model_with_same_filehash in models_with_same_filehash:
                    if model_with_same_filehash["model_user_id"] == user.user_id and model_with_same_filehash["model_state"] == "completed":
                        response["success"]["model_already_exists_name"] = model_with_same_filehash["model_name"]
                        response["success"]["message"] = "Já existe um projeto com este arquivo chamado: "
                        response["success"]["models_ids"].append(model_with_same_filehash["model_id"])
                        model_already_exits = True
                        break

            if model_already_exits:
                continue
            else:
                response["success"]["message"] = "Upload realizado com sucesso."

            if index == 0:
                model = Dynamo().get_model(self.get_model_id_from_uploaded_file(uploaded_file))
            else:
                model = self.generate_new_model(user, os.path.basename(ifc_location))

            ReadWrite().zip_file(ifc_location, lambda_constants["tmp_path"] + "file_ok.zip")

            model["model_name"] = os.path.basename(ifc_location)
            model["model_filename"] = os.path.basename(ifc_location)
            model["model_filehash"] = ReadWrite().get_file_hash(ifc_location)

            model_uploaded_filename = Generate().generate_short_id()
            model["model_filename_zip"] = model_uploaded_filename + ".zip"
            model["model_upload_path_zip"] = model["model_upload_path"] + model["model_filename_zip"]
            S3().upload_file(lambda_constants["processed_bucket"], model["model_upload_path_zip"], lambda_constants["tmp_path"] + "file_ok.zip")

            model["model_format"] = file_format
            model["model_filesize"] = str(os.path.getsize(ifc_location))
            model["model_filesize_zip"] = str(os.path.getsize(lambda_constants["tmp_path"] + "file_ok.zip"))
            model["model_share_link"] = lambda_constants["domain_name_url"] + "/webview/?model_code=" + model["model_code"]
            if model["model_format"] in ["fbx", "glb"]:
                model["model_upload_path_glb"] = model["model_upload_path_zip"].replace(".zip", "-glb.zip")
                if model["model_format"] == "glb":
                    ReadWrite().zip_file(ifc_location, lambda_constants["tmp_path"] + "zipped_glb.zip")
                    S3().upload_file(lambda_constants["processed_bucket"], model["model_upload_path_glb"], lambda_constants["tmp_path"] + "zipped_glb.zip")
            elif model["model_format"] in ["ifc"]:
                model["model_upload_path_xml"] = model["model_upload_path_zip"].replace(".zip", "-xml.zip")
                model["model_upload_path_aug"] = model["model_upload_path_zip"].replace(".zip", "-aug.zip")
                model["model_upload_path_sd_aug"] = model["model_upload_path_zip"].replace(".zip", "-aug-sd.zip")
            model["model_share_link_qrcode"] = lambda_constants["processed_bucket_cdn"] + "/" + model["model_upload_path_zip"].replace(model_uploaded_filename, "QRSHARE-" + model_uploaded_filename).replace(".zip", ".png")
            Generate().generate_qr_code(model["model_share_link"], lambda_constants["processed_bucket"], model["model_upload_path_zip"].replace(model_uploaded_filename, "QRSHARE-" + model_uploaded_filename).replace(".zip", ".png"))

            post_data = {"branch_key": lambda_constants["branch_key"], "channel": "app", "feature": "app", "campaign": "app", "stage": "sharing", "tags": [model["model_name"], model["model_id"]], "data": {"$canonical_identifier": "user/" + str(model["model_id"]), "$og_title": model["model_name"], "$og_description": model["model_name"], "$og_image_url": "", "$desktop_url": "https://augin.app", "asset_type": "4", "user_id": user.user_id}}
            branch_response = Http().call_branch("POST", "url", post_data)
            model["model_branch_id"] = Http().get_branch_id(branch_response["url"])
            model["model_branch_url"] = branch_response["url"]
            model["model_branch_url_qrcode"] = lambda_constants["processed_bucket_cdn"] + "/" + model["model_upload_path_zip"].replace(model_uploaded_filename, "QRBRANCH-" + model_uploaded_filename).replace(".zip", ".png")
            Generate().generate_qr_code(model["model_branch_url"], lambda_constants["processed_bucket"], model["model_upload_path_zip"].replace(model_uploaded_filename, "QRBRANCH-" + model_uploaded_filename).replace(".zip", ".png"))

            response["success"]["models_ids"].append(model["model_id"])
            Dynamo().put_entity(model)
        return response

    def process_model_file_uploaded(self, model, federated_model=None):
        if not S3().check_if_file_exists(lambda_constants["processed_bucket"], model["model_upload_path_zip"]):
            return {"error": "Este model não foi enviado/transferido para a AWS."}

        model = self.change_model_state(model, "not_created", "in_processing")
        if model["model_format"] == "ifc":
            model_filesize_in_megabytes = StrFormat().format_bytes_to_megabytes(model["model_filesize"])
            ec_requested_gbs = self.generate_ec_requested_gbs(model_filesize_in_megabytes)
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

        elif model["model_format"] == "fbx":
            Lambda().invoke("fbx-to-glb-converter-lambda-dev", "Event", {"model_id": model["model_id"], "input_bucket": lambda_constants["processed_bucket"], "input_key": model["model_upload_path_zip"], "output_bucket": lambda_constants["processed_bucket"], "output_key": model["model_upload_path_glb"], "output_project_domain_name": lambda_constants["prefix_name"] + lambda_constants["domain_name"] + lambda_constants["sufix_name"]})

        # ec2_instances["ec2_instances"].remove(choose_ec2_instance)
        # Dynamo().put_entity(ec2_instances)
        if model["model_format"] == "ifc" and federated_model:
            model["model_used_in_federated_ids"].append(federated_model["model_id"])
        model["model_processing_started"] = True
        Dynamo().put_entity(model)
        data = {"model_id": model["model_id"], "output_format": "process_started"}
        Http().request("POST", "https://" + lambda_constants["prefix_name"] + lambda_constants["domain_name"] + lambda_constants["sufix_name"] + "/api/update_model_process", headers={}, data=data)

        if model["model_format"] == "glb":
            data = {"model_id": model["model_id"], "output_format": "glb"}
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

    def change_model_state(self, model, current_status, next_status):
        model["model_user_id_state"] = model["model_user_id_state"].replace(current_status, next_status)
        model["model_state"] = model["model_state"].replace(current_status, next_status)
        return model

    def generate_ec_requested_gbs(self, model_filesize_in_megabytes):
        mbs_converted = model_filesize_in_megabytes / 25
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
            return False

    def is_glb_file(self, file_path):
        try:
            with open(file_path, "rb") as f:  # Read as binary
                header = f.read(4)  # Read first 4 bytes to get the magic number
                return header == b"glTF"
        except Exception as e:
            return False

    def is_zip_using_magic_number(self, filename):
        with open(filename, "rb") as f:
            magic_number = f.read(4)
        return magic_number in [b"\x50\x4B\x03\x04", b"\x50\x4B\x05\x06", b"\x50\x4B\x07\x08"]

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
