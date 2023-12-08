import time
import requests
import json
import gzip
import base64

from datetime import datetime
from utils.Config import lambda_constants
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Ses import Ses
from utils.AWS.S3 import S3
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Generate import Generate
from objects.Order import generate_order_nfse_pre_number
from objects.PendingNfse import PendingNfse
from objects.User import load_user

### TODO CHANGE VARIABLES WHEN IN PROD
# senfin_url = "https://sefin.nfse.gov.br/sefinnacional"
# tpAmb = "1"
# verAplic = "lhp 1.0"
senfin_url = "https://sefin.producaorestrita.nfse.gov.br/SefinNacional"
tpAmb = "2"
verAplic = "SefinNac_Pre_1.0.0"

cert_path = "xmls/augin_certificate.pem"
key_path = "xmls/augin_decrypted_privatekey.pem"
pfx_path = "xmls/augin_key.pfx"
pfx_password = "Augin2019"


class BillingController:
    def __init__(self) -> None:
        pass

    def generate_and_send_orders_nfses(self):
        import shutil
        import os
        from datetime import datetime, timedelta

        ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])

        first_day_this_month = datetime.today().replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        last_month = last_day_last_month.strftime("%m")
        last_month_year = last_day_last_month.strftime("%Y")

        nfses_from_last_month = S3().list_files_from_folder(lambda_constants["processed_bucket"], "nfse/" + last_month_year + "/" + last_month + "/")
        if not nfses_from_last_month:
            return
        if not os.path.exists(lambda_constants["tmp_path"] + "nfses_to_be_zipped"):
            os.makedirs(lambda_constants["tmp_path"] + "nfses_to_be_zipped")
        for nfse in nfses_from_last_month:
            S3().download_file(lambda_constants["processed_bucket"], nfse["Key"], lambda_constants["tmp_path"] + "nfses_to_be_zipped/" + nfse["Key"].split("/")[-1])
        shutil.make_archive(lambda_constants["tmp_path"] + lambda_constants["project_name"] + " NFSES " + last_month + "-" + last_month_year, "zip", lambda_constants["tmp_path"] + "nfses_to_be_zipped")
        nfses_key = "nfses_report/nfses_report_" + last_month + "_" + last_month_year + "_" + Generate().generate_short_id() + ".zip"
        S3().upload_file(lambda_constants["processed_bucket"], nfses_key, lambda_constants["tmp_path"] + lambda_constants["project_name"] + " NFSES " + last_month + "-" + last_month_year + ".zip")

        Ses().send_email_with_attachment(["eugenio@devesch.com.br", "leo@devesch.com.br"], lambda_constants["project_name"] + " NFSES " + last_month + "-" + last_month_year, "<p>" + lambda_constants["project_name"] + " NFSES " + last_month + "-" + last_month_year + "</p>", lambda_constants["project_name"] + " NFSES " + last_month + "-" + last_month_year + ".zip", lambda_constants["processed_bucket"], nfses_key, region=lambda_constants["region"])
        ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])

    def check_and_issued_not_issued_bill_of_sales(self):
        pending_nfse_orders = Dynamo().query_pending_nfse_orders()
        if pending_nfse_orders:
            for pending_nfse in pending_nfse_orders:
                order = Dynamo().get_order(pending_nfse["pending_nfse_order_id"])
                order_user = load_user(pending_nfse["pending_nfse_order_user_id"])
                if order and order_user:
                    if order["order_status"] == "paid" and order["order_nfse_status"] == "not_issued":
                        self.generate_bill_of_sale(order_user, order)
                    order = Dynamo().get_order(pending_nfse["pending_nfse_order_id"])
                    if order["order_nfse_status"] == "issued":
                        Dynamo().delete_entity(pending_nfse)
        return

    def get_bill_of_sale_events(self, order):
        response = self.get_nfse_eventos_by_chave_acesso(order["order_nfse_id"])
        print("HERE")

    def cancel_bill_of_sale(self, order):
        new_cancel_nfse_with_data = self.generate_new_cancel_nfse(order)
        cancel_nfe_with_data_signed = self.sign_xml_element(new_cancel_nfse_with_data, element="PedReg")
        ReadWrite().write_file_with_codecs(lambda_constants["tmp_path"] + "new_cancel_nfse_with_data_signed.xml", cancel_nfe_with_data_signed)
        cancel_nfe_with_data_signed_gzipped = self.compress_to_gzip_and_base64_encode(ReadWrite().read_file_with_codecs(lambda_constants["tmp_path"] + "new_cancel_nfse_with_data_signed.xml"))
        ReadWrite().write_file_with_codecs(lambda_constants["tmp_path"] + "new_cancel_nfse_with_data_signed_gzipped.xml", cancel_nfe_with_data_signed_gzipped)

        cancel_nfse = self.send_cancel_nfse_to_api(order["order_nfse_id"], cancel_nfe_with_data_signed_gzipped)
        if "erros" in cancel_nfse:
            return

        Dynamo().update_entity(order, "order_nfse_status", "canceled")
        Dynamo().update_entity(order, "order_nfse_canceled_at", str(time.time()))
        S3().delete_file(lambda_constants["processed_bucket"], order["order_nfse_xml_link"].replace(lambda_constants["processed_bucket_cdn"] + "/", ""))
        S3().delete_file(lambda_constants["processed_bucket"], order["order_nfse_pdf_link"].replace(lambda_constants["processed_bucket_cdn"] + "/", ""))
        Dynamo().update_entity(order, "order_nfse_xml_link", "")
        Dynamo().update_entity(order, "order_nfse_pdf_link", "")

    def get_bill_of_sale_xml(self, order):
        get_nfse = self.get_nfse_by_chave_acesso(order["order_nfse_id"])
        str_nfse = self.decompress_from_gzip_and_base64_encode(get_nfse["nfseXmlGZipB64"])
        return str_nfse

    def save_bill_of_sale_xml(self, order):
        get_nfse = self.get_nfse_by_chave_acesso(order["order_nfse_id"])
        str_nfse = self.decompress_from_gzip_and_base64_encode(get_nfse["nfseXmlGZipB64"])
        ReadWrite().write_file_with_codecs(lambda_constants["tmp_path"] + "nfse.xml", str_nfse)
        S3().upload_file(lambda_constants["processed_bucket"], self.generate_nfse_processed_bucket_key(order["order_id"]), lambda_constants["tmp_path"] + "nfse.xml")
        Dynamo().update_entity(order, "order_nfse_xml_link", lambda_constants["processed_bucket_cdn"] + "/" + self.generate_nfse_processed_bucket_key(order["order_id"]))

    def save_bill_of_sale_pdf(self, order):
        binary_bill_of_sale_pdf = self.get_danfe_by_chave_acesso(order["order_nfse_id"])
        ReadWrite().write_bytes(binary_bill_of_sale_pdf, lambda_constants["tmp_path"] + "nfse.pdf")
        S3().upload_file(lambda_constants["processed_bucket"], self.generate_nfse_processed_bucket_key(order["order_id"], extension=".pdf"), lambda_constants["tmp_path"] + "nfse.pdf")
        Dynamo().update_entity(order, "order_nfse_pdf_link", lambda_constants["processed_bucket_cdn"] + "/" + self.generate_nfse_processed_bucket_key(order["order_id"], extension=".pdf"))

    def generate_bill_of_sale(self, user, order):
        # self.extract_cert_and_key_from_pfx(pfx_path, pfx_password, cert_path, key_path)
        order = generate_order_nfse_pre_number(order)
        new_emit_nfse_with_data = self.generate_new_emit_nfse(user, order)
        nfe_with_data_signed = self.sign_xml_element(new_emit_nfse_with_data)
        ReadWrite().write_file_with_codecs(lambda_constants["tmp_path"] + "new_emit_nfse_with_data_signed.xml", nfe_with_data_signed)
        nfe_with_data_signed_gzipped = self.compress_to_gzip_and_base64_encode(nfe_with_data_signed)
        ReadWrite().write_file_with_codecs(lambda_constants["tmp_path"] + "new_emit_nfse_with_data_signed_gzipped.xml", nfe_with_data_signed_gzipped)

        emit_nfse = self.send_emit_nfse_to_api(nfe_with_data_signed_gzipped)
        if emit_nfse.get("erros"):
            self.send_unable_to_generate_nfse_email(str(emit_nfse["erros"]))
            Dynamo().put_entity(PendingNfse(order["order_id"], order["order_user_id"]).__dict__)
            return

        if emit_nfse.get("chaveAcesso"):
            order["order_nfse_id"] = emit_nfse["chaveAcesso"]
            Dynamo().update_entity(order, "order_nfse_id", emit_nfse["chaveAcesso"])
            Dynamo().update_entity(order, "order_nfse_status", "issued")
            Dynamo().update_entity(order, "order_nfse_created_at", str(time.time()))
            self.save_bill_of_sale_pdf(order)
            self.save_bill_of_sale_xml(order)

    def generate_new_emit_nfse(self, user, order):
        xml = ReadWrite().read_file_with_codecs("xmls/new_emit_nfse_no_data.xml")
        xml = xml.replace("{{cnpj_val}}", lambda_constants["cnpj"])
        xml = xml.replace("{{tpAmb_val}}", tpAmb)
        xml = xml.replace("{{verAplic_val}}", verAplic)
        xml = xml.replace("{{email_sender_val}}", lambda_constants["email_sender"])
        xml = xml.replace("{{phone_val}}", lambda_constants["phone"])
        xml = xml.replace("{{order_nfse_number_val}}", order["order_nfse_number"])
        xml = xml.replace("{{actual_billing_time_val}}", self.format_unix_to_billing_time(time.time()))
        xml = xml.replace("{{actual_billing_date_val}}", self.format_unix_to_billing_time(time.time(), date_only=True))

        if user.user_client_type == "physical":
            ### TODO RETURN TO CPF WHEN PROD
            # xml = xml.replace("{{CNPJ_or_CPF_val}}", "<CPF>" + user.user_cpf + "</CPF>")
            xml = xml.replace("{{CNPJ_or_CPF_val}}", "<CNPJ>40178198000112</CNPJ>")
        elif user.user_client_type == "company":
            xml = xml.replace("{{CNPJ_or_CPF_val}}", "<CNPJ>" + user.user_cnpj + "</CNPJ>")

        xml = xml.replace("{{user_name_val}}", user.user_name)
        xml = xml.replace("{{user_city_code_val}}", user.user_address_data["user_city_code"])
        xml = xml.replace("{{user_zip_code_val}}", user.user_address_data["user_zip_code"])
        xml = xml.replace("{{user_street_val}}", user.user_address_data["user_street"])
        xml = xml.replace("{{user_street_number_val}}", user.user_address_data["user_street_number"])
        xml = xml.replace("{{user_neighborhood_val}}", user.user_address_data["user_neighborhood"])
        if user.user_address_data["user_complement"]:
            xml = xml.replace("{{user_complement_val}}", user.user_address_data["user_complement"])
        else:
            xml = xml.replace("{{user_complement_val}}", "Não informado")

        xml = xml.replace("{{order_price_val}}", self.convert_order_price_to_billing_price(order["order_total_price"]))
        ReadWrite().write_file_with_codecs(lambda_constants["tmp_path"] + "new_emit_nfse_with_data.xml", xml)
        return str(xml)

    def generate_new_cancel_nfse(self, order):
        xml = ReadWrite().read_file_with_codecs("xmls/new_cancel_nfse_no_data.xml")
        xml = xml.replace("{{verAplic_val}}", verAplic)
        xml = xml.replace("{{cnpj_val}}", lambda_constants["cnpj"])
        xml = xml.replace("{{tpAmb_val}}", tpAmb)
        xml = xml.replace("{{order_nfse_id_val}}", order["order_nfse_id"])
        xml = xml.replace("{{actual_billing_time_val}}", self.format_unix_to_billing_time(time.time()))
        xml = xml.replace("{{order_nfse_number_val}}", order["order_nfse_number"])
        ReadWrite().write_file_with_codecs(lambda_constants["tmp_path"] + "new_cancel_nfse_with_data.xml", xml)
        return str(xml)

    def sign_xml_element(self, xml_data, element="DPS"):
        from signxml import XMLSigner, methods
        from lxml import etree
        from cryptography import x509
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend

        root = etree.fromstring(xml_data.encode("utf-8"))

        if element == "DPS":
            infDPS_element = root.find(".//{http://www.sped.fazenda.gov.br/nfse}infDPS")
            if infDPS_element is None or not infDPS_element.get("Id"):
                raise ValueError("infDPS element with Id attribute not found in the XML.")
            inf_id = infDPS_element.get("Id")
        elif element == "PedReg":
            infPedReg_element = root.find(".//{http://www.sped.fazenda.gov.br/nfse}infPedReg")
            if infPedReg_element is None or not infPedReg_element.get("Id"):
                raise ValueError("infPedReg element with Id attribute not found in the XML.")
            inf_id = infPedReg_element.get("Id")

        with open(cert_path, "rb") as f:
            cert_data = f.read()
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())

        with open(key_path, "rb") as f:
            key_data = f.read()
        key = serialization.load_pem_private_key(key_data, password=None, backend=default_backend())

        signer = XMLSigner(method=methods.enveloped, signature_algorithm="rsa-sha1", digest_algorithm="sha1", c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
        signer.excise_empty_xmlns_declarations = True
        ns = {}
        ns[None] = signer.namespaces["ds"]
        signer.namespaces = ns

        signed_root = signer.sign(root, key=key, cert=cert.public_bytes(serialization.Encoding.PEM), reference_uri=f"#{inf_id}")
        signed_xml_str = etree.tostring(signed_root, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")
        return signed_xml_str

    def compress_to_gzip_and_base64_encode(self, xml_string):
        utf8_encoded_xml = xml_string.encode("utf-8")
        compressed_xml = gzip.compress(utf8_encoded_xml)
        decompressed_xml = gzip.decompress(compressed_xml)
        ReadWrite().write_file_with_codecs(lambda_constants["tmp_path"] + "new_emit_nfse_with_data_signed_decompressed.xml", decompressed_xml.decode("utf-8"))
        base64_encoded_xml = base64.b64encode(compressed_xml).decode("utf-8")
        return base64_encoded_xml

    def decompress_from_gzip_and_base64_encode(self, base64_encoded_xml):
        compressed_xml = base64.b64decode(base64_encoded_xml)
        decompressed_xml = gzip.decompress(compressed_xml)
        xml_string = decompressed_xml.decode("utf-8")
        return xml_string

    def send_emit_nfse_to_api(self, compressed_xml_b64):
        response = requests.post(f"{senfin_url}/nfse", json={"dpsXmlGZipB64": compressed_xml_b64}, cert=(cert_path, key_path), headers={"Content-Type": "application/json; charset=utf-8"})
        return json.loads(response.text)

    def send_cancel_nfse_to_api(self, chave_acesso, compressed_xml_b64):
        response = requests.post(f"{senfin_url}/nfse", json={"dpsXmlGZipB64": compressed_xml_b64}, cert=(cert_path, key_path), headers={"Content-Type": "application/json; charset=utf-8"})
        return json.loads(response.text)

    def get_nfse_eventos_by_chave_acesso(self, chave_acesso):
        response = requests.get(f"{senfin_url}/nfse/{chave_acesso}/eventos", cert=(cert_path, key_path), headers={"Content-Type": "application/json; charset=utf-8"})
        return json.loads(response.text)

    def get_nfse_by_chave_acesso(self, chave_acesso):
        response = requests.get(f"{senfin_url}/nfse/{chave_acesso}", cert=(cert_path, key_path), headers={"Content-Type": "application/json; charset=utf-8"})
        return json.loads(response.text)

    def get_danfe_by_chave_acesso(self, chave_acesso):
        response = requests.get(f"{senfin_url}/danfse/{chave_acesso}", cert=(cert_path, key_path), headers={"Content-Type": "application/json; charset=utf-8"})
        return response._content

    def send_unable_to_generate_nfse_email(self, emit_nfse_erros):
        Ses().send_email("eugenio@devesch.com.br", body_html="<p>" + emit_nfse_erros + "</p>", body_text="<p>" + emit_nfse_erros + "</p>", subject_data="Unable to generate nfse in " + lambda_constants["domain_name"], region=lambda_constants["region"])

    def generate_nfse_canceled_processed_bucket_key(self, order_id, extension=".xml"):
        return "nfse_canceled/" + datetime.fromtimestamp(int(float(time()))).strftime("%Y/%m") + "/" + order_id + extension

    def generate_nfse_processed_bucket_key(self, order_id, order_nfse_created_at=False, extension=".xml"):
        if order_nfse_created_at:
            return "nfse/" + datetime.fromtimestamp(int(float(order_nfse_created_at))).strftime("%Y/%m") + "/" + order_id + extension
        return "nfse/" + datetime.fromtimestamp(int(float(time.time()))).strftime("%Y/%m") + "/" + order_id + extension

    def format_unix_to_billing_time(self, unixtime, date_only=False):
        dt = datetime.utcfromtimestamp(unixtime)
        if date_only:
            return dt.strftime("%Y-%m-%d")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")

    def convert_order_price_to_billing_price(self, order_total_brl_price):
        return "{:.2f}".format(int(order_total_brl_price) / 100)

    def extract_cert_and_key_from_pfx(self, pfx_path, pfx_password, cert_path, key_path):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.serialization import pkcs12
        from cryptography.hazmat.backends import default_backend

        with open(pfx_path, "rb") as f:
            pfx_data = f.read()

        private_key, certificate, _ = pkcs12.load_key_and_certificates(pfx_data, pfx_password.encode(), backend=default_backend())

        with open(cert_path, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))

        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption()))
