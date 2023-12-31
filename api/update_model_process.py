import time
from python_web_frame.base_page import BasePage
from python_web_frame.controllers.model_controller import ModelController
from python_web_frame.controllers.project_controller import ProjectController
from objects.AnalyticsNewProjectPublished import AnalyticsNewProjectPublished
from objects.AnalyticsUserRegisteredInLast30DaysAndPublished import check_and_save_user_registered_in_last_30d_and_published_analytics
from utils.AWS.Dynamo import Dynamo
from utils.AWS.S3 import S3
from utils.Config import lambda_constants
from objects.User import load_user
from objects.UserNotification import create_notification_model_processed


class UpdateModelProcess(BasePage):
    def run(self):
        model = Dynamo().get_model(self.post["model_id"])
        if self.post.get("error"):
            ModelController().mark_model_as_error(model, self.post["error"])
            return {"success": "Model changed state to error"}

        if self.post["output_format"] == "model_aug_percent":
            if not model["model_aug_completed"]:
                model["model_aug_percent"] = self.post["progress_percent"]
                Dynamo().update_entity(model, "model_aug_percent", model["model_aug_percent"])
        elif self.post["output_format"] == "model_aug_sd_percent":
            if not model["model_aug_sd_completed"]:
                model["model_aug_sd_percent"] = self.post["progress_percent"]
                Dynamo().update_entity(model, "model_aug_sd_percent", model["model_aug_sd_percent"])

        elif self.post["output_format"] == "model_xml_started":
            model["model_xml_started"] = str(time.time())
            Dynamo().update_entity(model, "model_xml_started", model["model_xml_started"])
        elif self.post["output_format"] == "model_aug_started":
            model["model_aug_started"] = str(time.time())
            Dynamo().update_entity(model, "model_aug_started", model["model_aug_started"])
        elif self.post["output_format"] == "model_aug_sd_started":
            model["model_aug_sd_started"] = str(time.time())
            Dynamo().update_entity(model, "model_aug_sd_started", model["model_aug_sd_started"])

        elif self.post["output_format"] == "xml_to_dynamo":
            model["model_xml_to_dynamo_completed"] = str(time.time())
            model["model_valid_until"] = int(time.time()) + 10400000
            Dynamo().update_entity(model, "model_xml_to_dynamo_completed", model["model_xml_to_dynamo_completed"])
            Dynamo().update_entity(model, "model_valid_until", model["model_valid_until"], type="N")

        elif self.post["output_format"] == "xml":
            model["model_xml_completed"] = str(time.time())
            model["model_xml_memory_usage"] = str(self.post["max_memory_usage"])
            model["model_xml_to_dynamo_start"] = str(time.time())
            if self.post.get("ec2_machine"):
                model["model_xml_ec2_machine"] = str(self.post["ec2_machine"])
                Dynamo().update_entity(model, "model_xml_ec2_machine", model["model_xml_ec2_machine"])
            Dynamo().update_entity(model, "model_xml_memory_usage", model["model_xml_memory_usage"])
            Dynamo().update_entity(model, "model_xml_completed", model["model_xml_completed"])
            Dynamo().update_entity(model, "model_xml_to_dynamo_start", model["model_xml_to_dynamo_start"])
            ProjectController().add_project_to_process_xml_to_dynamo(self.post["model_id"], self.post["output_bucket"], self.post["output_key"], self.event.requestContext["domainName"])
            ModelController().generate_bin_files(model, self.post["output_bucket"], self.post["output_key"])

        elif self.post["output_format"] == "aug":
            model["model_aug_completed"] = str(time.time())
            model["model_aug_memory_usage"] = str(self.post["max_memory_usage"])
            if self.post.get("ec2_machine"):
                model["model_aug_ec2_machine"] = str(self.post["ec2_machine"])
                Dynamo().update_entity(model, "model_aug_ec2_machine", model["model_aug_ec2_machine"])
            Dynamo().update_entity(model, "model_aug_memory_usage", model["model_aug_memory_usage"])
            Dynamo().update_entity(model, "model_aug_completed", model["model_aug_completed"])

        elif self.post["output_format"] == "aug_sd":
            model["model_aug_sd_completed"] = str(time.time())
            model["model_aug_sd_memory_usage"] = str(self.post["max_memory_usage"])
            if self.post.get("ec2_machine"):
                model["model_aug_sd_ec2_machine"] = str(self.post["ec2_machine"])
                Dynamo().update_entity(model, "model_aug_sd_ec2_machine", model["model_aug_sd_ec2_machine"])
            Dynamo().update_entity(model, "model_aug_sd_memory_usage", model["model_aug_sd_memory_usage"])
            Dynamo().update_entity(model, "model_aug_sd_completed", model["model_aug_sd_completed"])

        elif self.post["output_format"] == "glb":
            model["model_xml_started"] = str(time.time())
            model["model_aug_started"] = str(time.time())
            model["model_aug_sd_started"] = str(time.time())
            model["model_xml_to_dynamo_start"] = str(time.time())
            model["model_xml_to_dynamo_completed"] = str(time.time())
            model["model_xml_completed"] = str(time.time())
            model["model_aug_completed"] = str(time.time())
            model["model_aug_sd_completed"] = str(time.time())
            Dynamo().put_entity(model)

        model = Dynamo().get_model(self.post["model_id"])
        model["model_processing_percentage"] = ModelController().calculate_model_process_percentage(model)
        Dynamo().update_entity(model, "model_processing_percentage", model["model_processing_percentage"])

        if model["model_processing_percentage"] == "100":
            if model["model_format"] == "ifc":
                model["model_filesize_xml"] = str(S3().get_filesize(lambda_constants["processed_bucket"], model["model_upload_path_xml"]))
                model["model_filesize_aug"] = str(S3().get_filesize(lambda_constants["processed_bucket"], model["model_upload_path_aug"]))
                model["model_filesize_sd_aug"] = str(S3().get_filesize(lambda_constants["processed_bucket"], model["model_upload_path_sd_aug"]))

                model = ModelController().calculate_model_memory_usage_in_gbs(model)
                model = ModelController().calculate_model_total_time(model)

            elif model["model_format"] == "fbx":
                model["model_filesize_glb"] = str(S3().get_filesize(lambda_constants["processed_bucket"], model["model_upload_path_glb"]))

            model["model_processing"] = False

            model = ModelController().change_model_state(model, model["model_state"], "completed")
            Dynamo().put_entity(model)

            user = load_user(model["model_user_id"])
            user.add_model_to_user_dicts(model)
            create_notification_model_processed(model["model_user_id"], model["model_name"])

            if (float(model["model_processing_started_at"]) + 3600) > float(model["created_at"]):
                check_and_save_user_registered_in_last_30d_and_published_analytics(user.created_at)
                Dynamo().put_entity(AnalyticsNewProjectPublished().__dict__)

            if model["model_used_in_federated_ids"]:
                federated_model = ModelController().publish_federated_model(model["model_used_in_federated_ids"][0])
                if federated_model:
                    user.add_model_to_user_dicts(federated_model)

        return {"success": "Percentagem do modelo atualizada com sucesso"}
