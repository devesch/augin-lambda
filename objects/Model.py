import time


class Model:
    def __init__(self, model_user_id, model_id, model_project_id, model_state) -> None:
        self.pk = "model#" + model_id
        self.sk = "model#" + model_id
        self.model_id = model_id
        self.model_project_id = model_project_id
        self.model_user_id = model_user_id
        self.model_user_id_state = model_user_id + "#" + model_state
        self.model_folder_id = ""

        self.model_branch_id = ""
        self.model_branch_url = ""
        self.model_branch_url_qrcode = ""

        self.model_name = ""
        self.model_filehash = str(time.time())
        self.model_filename = ""
        self.model_filename_zip = ""
        self.model_format = ""
        self.model_is_federated = False

        self.model_used_in_federated_ids = []
        self.model_federated_required_ids = []

        self.model_upload_path_zip = ""
        self.model_upload_path_xml = ""
        self.model_upload_path_aug = ""
        self.model_upload_path_sd_aug = ""
        self.model_upload_path_bin = ""
        self.model_upload_path_mini_bin = ""
        self.model_upload_path_glb = ""

        self.model_filesize = "0"
        self.model_filesize_zip = "0"
        self.model_filesize_xml = "0"
        self.model_filesize_aug = "0"
        self.model_filesize_sd_aug = "0"
        self.model_filesize_bin = "0"
        self.model_filesize_mini_bin = "0"
        self.model_filesize_glb = "0"

        self.model_upload_path = ""
        self.model_category = ""

        self.model_password = ""
        self.model_is_accessible = False
        self.model_is_password_protected = False

        self.model_sw_version = ""
        self.model_plugin_version = ""
        self.model_thumb_filename = ""
        self.model_zip_key = ""
        self.model_share_link = ""
        self.model_share_link_qrcode = ""
        self.model_name = str(time.time())
        self.model_work = ""
        self.model_region = ""
        self.model_city = ""
        self.model_builder = ""
        self.model_category = ""
        self.model_city_region = ""
        self.model_xml_ec2_machine = ""
        self.model_aug_ec2_machine = ""
        self.model_aug_sd_ec2_machine = ""
        self.model_memory_usage_in_gbs = "0.0"
        self.model_was_processed_where = "lambda10gb"
        self.model_xml_started = ""
        self.model_xml_memory_usage = "0.0"
        self.model_xml_completed = ""
        self.model_xml_total_time = "0.0"
        self.model_xml_to_dynamo_start = ""
        self.model_xml_to_dynamo_completed = ""
        self.model_xml_to_dynamo_total_time = "0.0"
        self.model_aug_started = ""
        self.model_aug_percent = "0"
        self.model_aug_memory_usage = "0.0"
        self.model_aug_completed = ""
        self.model_aug_total_time = "0.0"
        self.model_aug_sd_started = ""
        self.model_aug_sd_percent = "0"
        self.model_aug_sd_memory_usage = "0.0"
        self.model_aug_sd_completed = ""
        self.model_aug_sd_total_time = "0.0"
        self.model_processing_total_time = "0.0"
        self.model_processing_percentage = "0"
        self.model_state = model_state
        self.model_valid_until = int(time.time()) + 10400000  ### 120 dias
        self.created_at = str(time.time())
        self.entity = "model"
