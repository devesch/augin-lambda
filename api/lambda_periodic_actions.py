from python_web_frame.base_page import BasePage
from python_web_frame.controllers.billing_controller import BillingController
from utils.Config import lambda_constants
from utils.utils.Validation import Validation
import os


class LambdaPeriodicActions(BasePage):
    def run(self):
        if not Validation().check_if_local_env():
            if not self.post.get("lambda_key"):
                return {"error": "no lambda_key in post"}
            if self.post["lambda_key"] != lambda_constants["lambda_periodic_actions_key"]:
                return {"error": "incorrect key in post"}

        BillingController().check_and_issued_not_issued_bill_of_sales()
        self.check_and_delete_not_created_projects()
        if int(self.utils.get_current_day()) == 1:
            self.generate_and_send_orders_nfses()
            self.fix_total_count()
        self.check_and_send_emails_to_pending_projects()
        return {"success": "all periodic actions completed"}

    def check_and_delete_old_files_in_download_bucket(self):
        files_in_upload_bucket = self.utils.list_files_from_s3_folder(lambda_constants["upload_bucket"])
        deleted_files_in_upload_bucket = 0
        if files_in_upload_bucket:
            for file in files_in_upload_bucket:
                if self.check_if_file_should_be_deleted(file["LastModified"]):
                    self.utils.delete_file_from_s3(lambda_constants["upload_bucket"], file["Key"])
                    deleted_files_in_upload_bucket += 1
        print(str(deleted_files_in_upload_bucket) + "/" + str(len(files_in_upload_bucket)) + " old files deleted in S3 upload bucket")

    def check_if_file_should_be_deleted(self, LastModified):
        if LastModified.day > 30:
            return True
        return False

    def check_and_delete_not_created_projects(self):
        not_created_projects = self.dynamo.query_all_projects_from_status("not_created")
        not_created_projects_deleted = 0
        if not_created_projects:
            for not_created_project in not_created_projects:
                if self.utils.check_if_not_created_project_should_be_deleted(not_created_project["created_at"]):
                    project = self.dynamo.get_entity(not_created_project["pk"], not_created_project["sk"])
                    project_path = self.utils.generate_project_img_bucket_path(project["project_id"], project["created_at"])
                    self.utils.delete_folder_from_s3(lambda_constants["img_bucket"], project_path)
                    self.dynamo.delete_entity(project)
                    self.decrease_backoffice_data_total_count("project")
                    not_created_projects_deleted += 1
        print(str(not_created_projects_deleted) + "/" + str(len(not_created_projects)) + " not created projects deleted")

    def check_and_send_emails_to_pending_projects(self):
        pending_projects = self.dynamo.query_all_projects_from_status("pending")
        expiration_advisory_email_sent = 0
        if pending_projects:
            for pending_project in pending_projects:
                if self.utils.check_if_project_should_be_deleted(pending_project["created_at"]):
                    project = self.dynamo.get_entity(pending_project["pk"], pending_project["sk"])
                    project_path = self.utils.generate_project_img_bucket_path(project["project_id"], project["created_at"])
                    self.utils.delete_folder_from_s3(lambda_constants["img_bucket"], project_path)
                    self.dynamo.delete_entity(project)
                    user_project = self.load_user(project["project_user_email"])
                    user_project.user_total_count_pending_projects = str(int(user_project.user_total_count_pending_projects) - 1)
                    self.dynamo.update_entity(user_project.__dict__, "user_total_count_pending_projects", user_project.user_total_count_pending_projects)
                    self.decrease_backoffice_data_total_count("project")
                elif self.utils.check_if_project_should_receive_expiration_email(pending_project["created_at"]):
                    project = self.dynamo.get_entity(pending_project["pk"], pending_project["sk"])
                    if project["project_expiration_advisory_email"] == "not_sent":
                        self.send_html_project_expiration_advisory_email(project["project_user_email"], project["project_name"])
                        self.dynamo.update_entity(project, "project_expiration_advisory_email", "sent")
                        expiration_advisory_email_sent += 1

        print("email sent to " + str(expiration_advisory_email_sent) + "/" + str(len(pending_projects)))

    def generate_and_send_orders_nfses(self):
        from time import time
        import shutil
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.application import MIMEApplication

        last_month_date = self.utils.get_last_month_date()
        last_month = str(last_month_date.month)
        if int(last_month) < 10:
            last_month = "0" + last_month
        last_mont_year = str(last_month_date.year)
        nfses_from_last_month = self.utils.list_files_from_s3_folder(lambda_constants["img_bucket"], "nfse/" + last_mont_year + "/" + last_month + "/")
        if not nfses_from_last_month:
            return
        if not os.path.exists(temp_path + "/nfses_to_be_zipped"):
            os.makedirs(temp_path + "/nfses_to_be_zipped")

        for nfse in nfses_from_last_month:
            self.utils.download_file_from_s3(lambda_constants["img_bucket"], nfse["Key"], temp_path + "/nfses_to_be_zipped/" + nfse["Key"].split("/")[-1])
        shutil.make_archive(temp_path + "/Magipix NFSES " + last_month + "-" + last_mont_year, "zip", temp_path + "/nfses_to_be_zipped")

        SENDER = "eugenio@devesch.com.br"
        RECEIVER = "eugenio@devesch.com.br"
        RECEIVER2 = "leo@devesch.com.br"
        CHARSET = "utf-8"
        msg = MIMEMultipart("mixed")
        msg["Subject"] = "ZIP das NFSES geradas em " + last_month + "/" + last_mont_year
        msg["From"] = SENDER
        msg["To"] = RECEIVER
        msg_body = MIMEMultipart("alternative")
        BODY_TEXT = "ZIP das NFSES geradas em " + last_month + "/" + last_mont_year
        BODY_HTML = "<h1> Zip em anexo </h1>"
        textpart = MIMEText(BODY_TEXT.encode(CHARSET), "plain", CHARSET)
        htmlpart = MIMEText(BODY_HTML.encode(CHARSET), "html", CHARSET)
        msg_body.attach(textpart)
        msg_body.attach(htmlpart)
        ATTACHMENT1 = temp_path + "/Magipix NFSES " + last_month + "-" + last_mont_year + ".zip"
        att1 = MIMEApplication(open(ATTACHMENT1, "rb").read())
        att1.add_header("Content-Disposition", "attachment", filename=os.path.basename(ATTACHMENT1))
        msg.attach(msg_body)
        msg.attach(att1)
        get_ses_client().send_raw_email(
            Source=SENDER,
            Destinations=[RECEIVER, RECEIVER2],
            RawMessage={
                "Data": msg.as_string(),
            },
            ConfigurationSetName="configset",
        )
        shutil.rmtree(temp_path + "/nfses_to_be_zipped")
        os.remove(temp_path + "/Magipix NFSES " + last_month + "-" + last_mont_year + ".zip")

    def send_html_project_expiration_advisory_email(self, user_email, project_name):
        html = self.utils.read_html("panel_projects/_codes/html_project_expiration_advisory_email")
        html.esc("project_name_val", project_name)
        get_ses_client().send_email(
            Destination={"ToAddresses": [user_email]},
            Message={
                "Body": {
                    "Html": {
                        "Charset": "utf-8",
                        "Data": str(html),
                    },
                    "Text": {
                        "Charset": "utf-8",
                        "Data": str(html),
                    },
                },
                "Subject": {
                    "Charset": "utf-8",
                    "Data": "Magipix - Seu projeto está próximo de expirar!",
                },
            },
            Source=lambda_constants["email_sender"],
            ConfigurationSetName="configset",
        )
        return True

    def fix_total_count(self):
        all_users = self.dynamo.query_entity("user")
        for user in all_users:
            pending_projects, last_evaluated_key = self.dynamo.query_paginated_projects_from_user(user["user_email"], "pending", limit=100000)
            self.dynamo.update_entity(user, "user_total_count_pending_projects", str(len(pending_projects)))
            published_project, last_evaluated_key = self.dynamo.query_paginated_projects_from_user(user["user_email"], "published", limit=100000)
            self.dynamo.update_entity(user, "user_total_count_published_projects", str(len(published_project)))
            credits_modifications, last_evaluated_key = self.dynamo.query_paginated_all_users_credits_modifications(user["user_email"], limit=100000)
            self.dynamo.update_entity(user, "user_total_count_credits_modifications", str(len(credits_modifications)))

        all_projects = self.dynamo.query_entity("project")
        for project in all_projects:
            project_balances, last_evaluated_key = self.dynamo.query_paginated_project_balance(project["project_id"], last_evaluated_key=None, limit=100000)
            self.dynamo.update_entity(project, "project_total_project_balance_count", str(len(project_balances)))

        all_orders = self.dynamo.query_entity("order")
        all_cupons = self.dynamo.query_entity("cupom")
        all_app_errors = self.dynamo.query_entity("app_error")

        backoffice_data = self.get_backoffice_data()
        backoffice_data["backoffice_data_total_project_count"] = str(len(all_projects))
        backoffice_data["backoffice_data_total_user_count"] = str(len(all_users))
        backoffice_data["backoffice_data_total_order_count"] = str(len(all_orders))
        backoffice_data["backoffice_data_total_cupon_count"] = str(len(all_cupons))
        backoffice_data["backoffice_data_total_app_error_count"] = str(len(all_app_errors))
        self.dynamo.put_entity(backoffice_data)
