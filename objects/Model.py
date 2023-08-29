import time


class Model:
    def __init__(self, user_email, model_id, model_project_id, model_state) -> None:
        self.pk = "user#" + user_email + "#model_state#" + model_state
        self.sk = "model#" + model_id
        self.model_id = model_id
        self.model_project_id = model_project_id
        self.model_user_email = user_email

        self.model_filename = ""
        self.model_filename_zip = ""
        self.model_format = ""

        self.model_filesize = ""
        self.model_filesize_zip = ""

        self.model_upload_path_zip = ""
        self.model_upload_path_xml = ""
        self.model_upload_path_aug = ""
        self.model_upload_path_sd_aug = ""

        self.model_upload_path = ""

        self.model_sw_version = ""
        self.model_plugin_version = ""
        self.model_thumb_filename = ""
        self.model_zip_key = ""
        self.model_share_link = ""
        self.model_share_link_qrcode = ""
        self.model_name = str(time.time())
        self.model_is_password_protected = False
        self.model_password = ""
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
