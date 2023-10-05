from python_web_frame.base_page import BasePage
from python_web_frame.controllers.billing_controller import BillingController
from utils.Config import lambda_constants
from utils.utils.Validation import Validation
from datetime import datetime
import os


class LambdaPeriodicActions(BasePage):
    def run(self):
        if not Validation().check_if_local_env():
            if not self.post.get("lambda_key"):
                return {"error": "no lambda_key in post"}
            if self.post["lambda_key"] != lambda_constants["lambda_periodic_actions_key"]:
                return {"error": "incorrect key in post"}

        BillingController().check_and_issued_not_issued_bill_of_sales()
        if datetime.today().day == 1:
            self.generate_and_send_orders_nfses()
            # self.fix_total_count()
        return {"success": "all periodic actions completed"}

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
        if not os.path.exists(lambda_constants["tmp_path"] + "/nfses_to_be_zipped"):
            os.makedirs(lambda_constants["tmp_path"] + "/nfses_to_be_zipped")

        for nfse in nfses_from_last_month:
            self.utils.download_file_from_s3(lambda_constants["img_bucket"], nfse["Key"], lambda_constants["tmp_path"] + "/nfses_to_be_zipped/" + nfse["Key"].split("/")[-1])
        shutil.make_archive(lambda_constants["tmp_path"] + "/Magipix NFSES " + last_month + "-" + last_mont_year, "zip", lambda_constants["tmp_path"] + "/nfses_to_be_zipped")

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
        ATTACHMENT1 = lambda_constants["tmp_path"] + "/Magipix NFSES " + last_month + "-" + last_mont_year + ".zip"
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
        shutil.rmtree(lambda_constants["tmp_path"] + "/nfses_to_be_zipped")
        os.remove(lambda_constants["tmp_path"] + "/Magipix NFSES " + last_month + "-" + last_mont_year + ".zip")

    # def fix_total_count(self):
    #     all_users = self.dynamo.query_entity("user")
    #     for user in all_users:
    #         pending_projects, last_evaluated_key = self.dynamo.query_paginated_projects_from_user(user["user_email"], "pending", limit=100000)
    #         self.dynamo.update_entity(user, "user_total_count_pending_projects", str(len(pending_projects)))
    #         published_project, last_evaluated_key = self.dynamo.query_paginated_projects_from_user(user["user_email"], "published", limit=100000)
    #         self.dynamo.update_entity(user, "user_total_count_published_projects", str(len(published_project)))
    #         credits_modifications, last_evaluated_key = self.dynamo.query_paginated_all_users_credits_modifications(user["user_email"], limit=100000)
    #         self.dynamo.update_entity(user, "user_total_count_credits_modifications", str(len(credits_modifications)))

    #     all_projects = self.dynamo.query_entity("project")
    #     for project in all_projects:
    #         project_balances, last_evaluated_key = self.dynamo.query_paginated_project_balance(project["project_id"], last_evaluated_key=None, limit=100000)
    #         self.dynamo.update_entity(project, "project_total_project_balance_count", str(len(project_balances)))

    #     all_orders = self.dynamo.query_entity("order")
    #     all_cupons = self.dynamo.query_entity("cupom")
    #     all_app_errors = self.dynamo.query_entity("app_error")

    #     backoffice_data = self.get_backoffice_data()
    #     backoffice_data["backoffice_data_total_project_count"] = str(len(all_projects))
    #     backoffice_data["backoffice_data_total_user_count"] = str(len(all_users))
    #     backoffice_data["backoffice_data_total_order_count"] = str(len(all_orders))
    #     backoffice_data["backoffice_data_total_cupon_count"] = str(len(all_cupons))
    #     backoffice_data["backoffice_data_total_app_error_count"] = str(len(all_app_errors))
    #     self.dynamo.put_entity(backoffice_data)
