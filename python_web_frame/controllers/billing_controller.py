import tempfile
import signxml
import xml.etree.ElementTree as ET
import urllib.request, http.client
from OpenSSL import crypto
from lxml import etree
from unicodedata import normalize
from signxml import XMLSigner
from suds.client import Client
from suds.transport.http import HttpTransport
from datetime import datetime
from time import time
from utils.Config import lambda_constants
from utils.AWS.Lambda import Lambda
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Ses import Ses
from utils.AWS.S3 import S3
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Generate import Generate
from utils.utils.StrFormat import StrFormat
from utils.utils.Date import Date
from objects.PendingNfse import PendingNfse
from objects.User import load_user


class HTTPSClientAuthHandler(urllib.request.HTTPSHandler):
    def __init__(self, key, cert):
        urllib.request.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return http.client.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)


class HttpAuthenticated(HttpTransport):
    def __init__(self, key, cert, endereco, *args, **kwargs):
        HttpTransport.__init__(self, *args, **kwargs)
        self.key = key
        self.cert = cert
        self.endereco = endereco

    def u2handlers(self):
        return [HTTPSClientAuthHandler(self.key, self.cert)]


certificado_path = "xmls/AUGIN_SOFTWARES_LTDA_34804848000195_1669811592939092000.pfx"
certificado_password = "639764418"
# certificado_path = "xmls/magipix_key.pfx"
# certificado_password = "p12345"

url = "https://nfse-hom.procempa.com.br/bhiss-ws/nfse?wsdl"  ### TEST URL
# url = "https://nfe.portoalegre.rs.gov.br/bhiss-ws/nfse?wsdl"  ### PROD URL
cabecalho = "<cabecalho xmlns=" + chr(34) + "http://www.abrasf.org.br/nfse.xsd" + chr(34) + " versao=" + chr(34) + "1.00" + chr(34) + "><versaoDados >1.00</versaoDados ></cabecalho>"


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
        shutil.make_archive(lambda_constants["tmp_path"] + "Augin NFSES " + last_month + "-" + last_month_year, "zip", lambda_constants["tmp_path"] + "nfses_to_be_zipped")
        nfses_key = "nfses_report_" + last_month + "_" + last_month_year + "_" + Generate().generate_short_id() + ".zip"
        S3().upload_file(lambda_constants["upload_bucket"], nfses_key, lambda_constants["tmp_path"] + "Augin NFSES " + last_month + "-" + last_month_year + ".zip")

        ### TODO ADD LEOS EMAIL TO NFSES
        Ses().send_email_with_attachment("eugenio@devesch.com.br", "Augin NFSES " + last_month + "-" + last_month_year, "<p>Augin NFSES " + last_month + "-" + last_month_year + "</p>", "Augin NFSES " + last_month + "-" + last_month_year + ".zip", lambda_constants["upload_bucket"], nfses_key, region=lambda_constants["region"])
        ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])

    def check_and_issued_not_issued_bill_of_sales(self):
        pending_nfse_orders = Dynamo().query_pending_nfse_orders()
        if pending_nfse_orders:
            for pending_nfse in pending_nfse_orders:
                order = Dynamo().get_order(pending_nfse["pending_nfse_order_id"])
                order_user = load_user(pending_nfse["pending_nfse_order_user_id"])
                if order and order_user:
                    if order["order_status"] == "paid" and order["order_nfse_status"] == "not_issued":
                        BillingController().generate_bill_of_sale(order_user, order)
                    order = Dynamo().get_order(pending_nfse["pending_nfse_order_id"])
                    if order["order_nfse_status"] == "issued":
                        Dynamo().delete_entity(pending_nfse)
        return

    def get_bill_of_sale_xml(self, order):
        get_nfe_with_data = self.generate_get_nfe_with_data(order)
        # ReadWrite().write_file(lambda_constants["tmp_path"] +"get_nfe_with_data.xml", get_nfe_with_data)

        key, cert = self.generate_key_and_cert(certificado_path, certificado_password, https=True)
        cliente = Client(url, transport=HttpAuthenticated(key=key, cert=cert, endereco=url))
        ConsultarNfsePorRps_return = cliente.service.ConsultarNfsePorRps(cabecalho, get_nfe_with_data)

        return ET.fromstring(ConsultarNfsePorRps_return)

    def generate_only_pdf_nfse(self, order):
        Dynamo().update_entity(order, "order_nfse_pdf_link", lambda_constants["processed_bucket_cdn"] + "/" + self.generate_pdf_nfse_processed_bucket_key(order["order_id"], order["order_nfse_created_at"]))
        self.generate_pdf_bill_of_sale(order["order_id"], order["order_nfse_created_at"])
        return

    def refund_bill_of_sale(self, order):
        cancel_nfe_with_data = self.generate_cancel_nfe_with_data(order["order_nfse_id"])
        ReadWrite().write_file(lambda_constants["tmp_path"] + "cancel_nfe_with_data.xml", cancel_nfe_with_data)

        key, cert = self.generate_key_and_cert(certificado_path, certificado_password, https=False)
        xml_element = etree.fromstring(ReadWrite().read_bytes(lambda_constants["tmp_path"] + "cancel_nfe_with_data.xml"))
        cancel_nfe_with_data_signed = self.sign_xml_element(xml_element, "pedidoCancelamento_" + order["order_nfse_id"], key, cert)
        ReadWrite().write_file(lambda_constants["tmp_path"] + "cancel_nfe_with_data_signed.xml", cancel_nfe_with_data_signed)
        cancel_nfe_with_data_signed = self.fix_cancel_nfe_with_data_signed_signature_position()

        key, cert = self.generate_key_and_cert(certificado_path, certificado_password, https=True)
        cliente = Client(url, transport=HttpAuthenticated(key=key, cert=cert, endereco=url))
        CancelarNfse_return = cliente.service.CancelarNfse(cabecalho, cancel_nfe_with_data_signed)
        response_xml = ET.fromstring(CancelarNfse_return)

        if not self.check_if_nfse_was_canceled(CancelarNfse_return):
            self.send_unable_to_generate_nfse_email(CancelarNfse_return)
            return

        Dynamo().update_entity(order, "order_nfse_status", "canceled")
        Dynamo().update_entity(order, "order_nfse_canceled_at", str(time()))
        Dynamo().update_entity(order, "order_nfse_xml_link", lambda_constants["processed_bucket_cdn"] + "/" + self.generate_nfse_canceled_processed_bucket_key(order["order_id"]))

        xml_tree = ET.ElementTree(response_xml)
        xml_tree.write(lambda_constants["tmp_path"] + "cancel_nfe_response.xml")
        nfse_xml = self.get_bill_of_sale_xml(order)
        xml_tree = ET.ElementTree(nfse_xml)
        xml_tree.write(lambda_constants["tmp_path"] + "xml_tree.xml")
        S3().upload_file(lambda_constants["processed_bucket"], self.generate_nfse_canceled_processed_bucket_key(order["order_id"]), lambda_constants["tmp_path"] + "xml_tree.xml")
        S3().delete_file(lambda_constants["processed_bucket"], self.generate_nfse_processed_bucket_key(order["order_id"], order["order_nfse_created_at"]))
        self.generate_pdf_bill_of_sale(order["order_id"], order["order_nfse_created_at"])
        return

    def generate_bill_of_sale(self, user, order):
        nfe_with_data_rps_only = self.generate_nfe_with_data_rps_only(user, order)
        ReadWrite().write_file(lambda_constants["tmp_path"] + "nfe_with_data_rps_only.xml", nfe_with_data_rps_only)

        key, cert = self.generate_key_and_cert(certificado_path, certificado_password, https=False)
        xml_element = etree.fromstring(ReadWrite().read_bytes(lambda_constants["tmp_path"] + "nfe_with_data_rps_only.xml"))
        nfe_with_data_rps_signed = self.sign_xml_element(xml_element, str(int(float(order["created_at"]))), key, cert)

        nfe_with_data_lote_only = self.generate_nfe_with_data_lote_only(order, nfe_with_data_rps_signed)
        ReadWrite().write_file(lambda_constants["tmp_path"] + "nfe_with_data_lote_only.xml", nfe_with_data_lote_only)

        xml_element = etree.fromstring(ReadWrite().read_bytes(lambda_constants["tmp_path"] + "nfe_with_data_lote_only.xml"))
        nfe_with_data_lote_signed = self.sign_xml_element(xml_element, "Lote" + str(int(float(order["created_at"]))), key, cert)
        nfe_with_data_lote_signed = self.fix_nfe_with_data_lote_signed_signature_position(nfe_with_data_lote_signed)
        ReadWrite().write_file(lambda_constants["tmp_path"] + "nfe_with_data_lote_signed.xml", nfe_with_data_lote_signed)

        try:
            key, cert = self.generate_key_and_cert(certificado_path, certificado_password, https=True)
            cliente = Client(url, transport=HttpAuthenticated(key=key, cert=cert, endereco=url))
            GerarNfse_return = cliente.service.GerarNfse(cabecalho, nfe_with_data_lote_signed)
            response_xml = ET.fromstring(GerarNfse_return)
        except Exception as e:
            self.send_unable_to_generate_nfse_email(e)
            pending_nfse = PendingNfse(order["order_id"], order["order_user_id"])
            Dynamo().put_entity(pending_nfse.__dict__)
            return

        if not self.check_if_nfse_was_issued(GerarNfse_return):
            self.send_unable_to_generate_nfse_email(str(GerarNfse_return))
            pending_nfse = PendingNfse(order["order_id"], order["order_user_id"])
            Dynamo().put_entity(pending_nfse.__dict__)
            return

        Dynamo().update_entity(order, "order_nfse_id", response_xml[3][0][0][0][0].text)
        Dynamo().update_entity(order, "order_nfse_status", "issued")
        Dynamo().update_entity(order, "order_nfse_number", response_xml[3][0][0][0][3][0].text)
        Dynamo().update_entity(order, "order_nfse_serie", response_xml[3][0][0][0][3][1].text)
        Dynamo().update_entity(order, "order_nfse_type", response_xml[3][0][0][0][3][2].text)
        Dynamo().update_entity(order, "order_nfse_created_at", str(time()))
        Dynamo().update_entity(order, "order_nfse_xml_link", lambda_constants["processed_bucket_cdn"] + "/" + self.generate_nfse_processed_bucket_key(order["order_id"]))
        Dynamo().update_entity(order, "order_nfse_pdf_link", lambda_constants["processed_bucket_cdn"] + "/" + self.generate_pdf_nfse_processed_bucket_key(order["order_id"]))
        order = Dynamo().get_order(order["order_id"])
        xml_tree = ET.ElementTree(response_xml)
        xml_tree.write(lambda_constants["tmp_path"] + "generated_nfe_response.xml")
        nfse_xml = self.get_bill_of_sale_xml(order)
        xml_tree = ET.ElementTree(nfse_xml)
        xml_tree.write(lambda_constants["tmp_path"] + "xml_tree.xml")
        S3().upload_file(lambda_constants["processed_bucket"], self.generate_nfse_processed_bucket_key(order["order_id"]), lambda_constants["tmp_path"] + "xml_tree.xml")
        self.generate_pdf_bill_of_sale(order["order_id"], None)
        return

    def generate_international_pdf_bill_of_sale(self, order):
        if self.generate_pdf_bill_of_sale(order["order_id"], order["created_at"]):
            Dynamo().update_entity(order, "order_nfse_pdf_link", lambda_constants["processed_bucket_cdn"] + "/" + self.generate_pdf_nfse_processed_bucket_key(order["order_id"]))
        S3().download_file(lambda_constants["processed_bucket"], self.generate_pdf_nfse_processed_bucket_key(order["order_id"]), lambda_constants["tmp_path"] + "order_pdf.pdf")
        S3().upload_file(lambda_constants["processed_bucket"], self.generate_nfse_processed_bucket_key(order["order_id"], extension=".pdf"), lambda_constants["tmp_path"] + "order_pdf.pdf")
        return

    def cancel_international_pdf_bill_of_sale(self, order):
        S3().delete_file(lambda_constants["processed_bucket"], self.generate_nfse_processed_bucket_key(order["order_id"], order["created_at"], extension=".pdf"))
        if self.generate_pdf_bill_of_sale(order["order_id"], order["created_at"]):
            Dynamo().update_entity(order, "order_nfse_pdf_link", lambda_constants["processed_bucket_cdn"] + "/" + self.generate_nfse_canceled_processed_bucket_key(order["order_id"], extension=".pdf"))
        S3().download_file(lambda_constants["processed_bucket"], self.generate_pdf_nfse_processed_bucket_key(order["order_id"], order["created_at"]), lambda_constants["tmp_path"] + "order_pdf.pdf")
        S3().upload_file(lambda_constants["processed_bucket"], self.generate_nfse_canceled_processed_bucket_key(order["order_id"], extension=".pdf"), lambda_constants["tmp_path"] + "order_pdf.pdf")
        return

    def generate_pdf_bill_of_sale(self, order_id, order_nfse_created_at):
        lambda_generate_pdf_response = Lambda().invoke("lambda_generate_pdf", "RequestResponse", {"input_url": lambda_constants["domain_name_url"] + "/backoffice_order_nfse_pdf/?order_id=" + order_id, "output_bucket": lambda_constants["processed_bucket"], "output_key": self.generate_pdf_nfse_processed_bucket_key(order_id, order_nfse_created_at)})
        if "error" in lambda_generate_pdf_response:
            return False
        return True

    def generate_get_nfe_with_data(self, order):
        xml = ReadWrite().read_file("xmls/get_nfe_no_data.xml")
        xml = xml.replace("{{order_nfse_number_val}}", order["order_nfse_number"])
        xml = xml.replace("{{order_nfse_serie_val}}", order["order_nfse_serie"])
        xml = xml.replace("{{order_nfse_type_val}}", order["order_nfse_type"])
        xml = xml.replace("{{company_cnpj_val}}", lambda_constants["cnpj"])
        xml = xml.replace("{{company_inscription_val}}", lambda_constants["municipal_inscription"])
        return self.remover_acentos(xml)

    def check_if_nfse_was_issued(self, GerarNfse_return):
        if len(GerarNfse_return) > 5000:
            return True
        return False

    def check_if_nfse_was_canceled(self, CancelarNfse_return):
        if len(CancelarNfse_return) > 5000:
            return True
        return False

    def generate_cancel_nfe_with_data(self, nfse_id):
        xml = ReadWrite().read_file("xmls/cancel_nfe_no_data.xml")
        xml = xml.replace("{{nfse_id_val}}", nfse_id)
        xml = xml.replace("{{company_cnpj_val}}", lambda_constants["cnpj"])
        xml = xml.replace("{{company_inscription_val}}", lambda_constants["municipal_inscription"])
        return self.remover_acentos(xml)

    def generate_nfse_processed_bucket_key(self, order_id, order_nfse_created_at=False, extension=".xml"):
        if order_nfse_created_at:
            return "nfse/" + datetime.fromtimestamp(int(float(order_nfse_created_at))).strftime("%Y/%m") + "/" + order_id + extension
        return "nfse/" + datetime.fromtimestamp(int(float(time()))).strftime("%Y/%m") + "/" + order_id + extension

    def generate_pdf_nfse_processed_bucket_key(self, order_id, order_nfse_created_at=False):
        if order_nfse_created_at:
            return "nfse_pdf/" + datetime.fromtimestamp(int(float(order_nfse_created_at))).strftime("%Y/%m") + "/" + order_id + ".pdf"
        return "nfse_pdf/" + datetime.fromtimestamp(int(float(time()))).strftime("%Y/%m") + "/" + order_id + ".pdf"

    def generate_nfse_canceled_processed_bucket_key(self, order_id, extension=".xml"):
        return "nfse_canceled/" + datetime.fromtimestamp(int(float(time()))).strftime("%Y/%m") + "/" + order_id + extension

    def fix_cancel_nfe_with_data_signed_signature_position(self):
        xml = ReadWrite().read_file(lambda_constants["tmp_path"] + "cancel_nfe_with_data_signed.xml")
        xml = xml.replace("</Pedido>", "")
        xml = xml.replace("</CancelarNfseEnvio>", "</Pedido></CancelarNfseEnvio>")
        return xml

    def fix_nfe_with_data_lote_signed_signature_position(self, xml):
        X509Certificate_data = xml.split("<X509Certificate>")[1]
        X509Certificate_data = xml.split("</X509Certificate>")[0]
        X509Certificate = "<X509Certificate>" + X509Certificate_data.split("<X509Certificate>")[1] + "</X509Certificate>"
        xml = xml.replace(X509Certificate, "")
        rps_split = xml.split("</X509Data></KeyInfo></Signature></Rps>")
        xml = rps_split[0] + X509Certificate + "</X509Data></KeyInfo></Signature></Rps>" + rps_split[1]
        lote_split = xml.split("<X509Data/></KeyInfo></Signature></GerarNfseEnvio>")
        xml = lote_split[0] + "<X509Data>" + X509Certificate + "</X509Data></KeyInfo></Signature></GerarNfseEnvio>" + lote_split[1]
        return xml

    def generate_nfe_with_data_lote_only(self, order, nfe_with_data_rps_signed):
        xml = ReadWrite().read_file("xmls/nfe_no_data_lote_only.xml")
        xml = xml.replace("{{order_id_val}}", str(int(float(order["created_at"]))))
        xml = xml.replace("{{company_cnpj_val}}", lambda_constants["cnpj"])
        xml = xml.replace("{{company_inscription_val}}", lambda_constants["municipal_inscription"])
        xml = xml.replace("{{rps_val}}", nfe_with_data_rps_signed)
        return self.remover_acentos(xml)

    def sign_xml_element(self, xml_element, reference, key, cert):
        for element in xml_element.iter("*"):
            if element.text is not None and not element.text.strip():
                element.text = None

        signer = XMLSigner(method=signxml.methods.enveloped, signature_algorithm="rsa-sha256", digest_algorithm="sha256", c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments")
        signer.excise_empty_xmlns_declarations = True
        ns = {}
        ns[None] = signer.namespaces["ds"]
        signer.namespaces = ns
        ref_uri = ("#%s" % reference) if reference else None
        signed_root = signer.sign(xml_element, key=key, cert=cert, reference_uri=ref_uri)
        ns = {"ns": "http://www.w3.org/2000/09/xmldsig#"}
        tagX509Data = signed_root.find(".//ns:X509Data", namespaces=ns)
        etree.SubElement(tagX509Data, "X509Certificate").text = cert
        return etree.tostring(signed_root, encoding="unicode", pretty_print=False)

    def remover_acentos(self, txt):
        return normalize("NFKD", txt).encode("ASCII", "ignore").decode("ASCII")

    def generate_key_and_cert(self, certificado_path, certificado_password, https=False):
        with open(certificado_path, "rb") as cert_arquivo:
            cert_conteudo = cert_arquivo.read()
        pkcs12 = crypto.load_pkcs12(cert_conteudo, certificado_password)
        if not https:
            cert = crypto.dump_certificate(crypto.FILETYPE_PEM, pkcs12.get_certificate()).decode("utf-8")
            cert = cert.replace("\n", "")
            cert = cert.replace("-----BEGIN CERTIFICATE-----", "")
            cert = cert.replace("-----END CERTIFICATE-----", "")
            chave = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkcs12.get_privatekey())
            return chave, cert
        if https:
            cert = crypto.dump_certificate(crypto.FILETYPE_PEM, pkcs12.get_certificate())
            chave = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkcs12.get_privatekey())
            with tempfile.NamedTemporaryFile(delete=False) as arqcert:
                arqcert.write(cert)
            with tempfile.NamedTemporaryFile(delete=False) as arqchave:
                arqchave.write(chave)
            return arqchave.name, arqcert.name

    def generate_nfe_with_data_rps_only(self, user, order):
        xml = ReadWrite().read_file("xmls/nfe_no_data_rps_only.xml")
        xml = xml.replace("{{order_id_val}}", str(int(float(order["created_at"]))))
        xml = xml.replace("{{order_created_at_val}}", Date().format_unixtime_to_billingtime(order["created_at"]))
        xml = xml.replace("{{order_total_price_val}}", StrFormat().format_to_billing_money(order["order_total_price"]))
        xml = xml.replace("{{order_iss_price_val}}", StrFormat().format_to_billing_money(str(int(int(order["order_total_price"]) * 0.02))))
        xml = xml.replace("{{order_commentary_val}}", order["order_descrimination"])
        xml = xml.replace("{{company_cnpj_val}}", lambda_constants["cnpj"])
        xml = xml.replace("{{company_inscription_val}}", lambda_constants["municipal_inscription"])

        if user.user_client_type == "physical":
            if user.user_cpf != "":
                xml = xml.replace("{{user_id_tag_val}}", "<Cpf>" + user.user_cpf + "</Cpf>")
            else:
                xml = xml.replace("{{user_id_tag_val}}", "<Cpf>00000000000</Cpf>")
                # xml = xml.replace("<IdentificacaoTomador>", "")
                # xml = xml.replace("</IdentificacaoTomador>", "")
                # xml = xml.replace("<CpfCnpj>", "")
                # xml = xml.replace("<CpfCnpj/>", "")

        elif user.user_client_type == "company":
            if user.user_cnpj != "":
                xml = xml.replace("{{user_id_tag_val}}", "<Cnpj>" + user.user_cnpj + "</Cnpj>")
            else:
                xml = xml.replace("{{user_id_tag_val}}", "<Cnpj>0</Cnpj>")
                # xml = xml.replace("<IdentificacaoTomador>", "")
                # xml = xml.replace("</IdentificacaoTomador>", "")
                # xml = xml.replace("<CpfCnpj>", "")
                # xml = xml.replace("<CpfCnpj/>", "")

        xml = xml.replace("{{user_full_name_val}}", (user.user_name).strip())

        if user.user_address_data["user_street"]:
            xml = xml.replace("{{user_street_val}}", user.user_address_data["user_street"])
        else:
            xml = xml.replace("{{user_street_val}}", "NAO INFORMADO")

        if user.user_address_data["user_street_number"]:
            xml = xml.replace("{{user_street_number_val}}", user.user_address_data["user_street_number"])
        else:
            xml = xml.replace("{{user_street_number_val}}", "S/N")

        if user.user_address_data["user_complement"]:
            xml = xml.replace("{{user_complement_val}}", user.user_address_data["user_complement"])
        else:
            xml = xml.replace("{{user_complement_val}}", "NAO INFORMADO")

        if user.user_address_data["user_neighborhood"]:
            xml = xml.replace("{{user_neighborhood_val}}", user.user_address_data["user_neighborhood"])
        else:
            xml = xml.replace("{{user_neighborhood_val}}", "NAO INFORMADO")

        if user.user_address_data["user_city_code"]:
            xml = xml.replace("{{user_city_code_val}}", user.user_address_data["user_city_code"])
        else:
            xml = xml.replace("{{user_city_code_val}}", "4314902")

        if user.user_address_data["user_state"]:
            xml = xml.replace("{{user_state_val}}", user.user_address_data["user_state"].upper())
        else:
            xml = xml.replace("{{user_state_val}}", "RS")

        if user.user_address_data["user_zip_code"]:
            xml = xml.replace("{{user_zip_code_val}}", user.user_address_data["user_zip_code"])
        else:
            xml = xml.replace("{{user_zip_code_val}}", "00000000")

        return self.remover_acentos(xml)

    def send_unable_to_generate_nfse_email(self, generate_nfse_response):
        Ses().send_email("eugenio@devesch.com.br", body_html="<p>" + generate_nfse_response + "</p>", body_text="<p>" + generate_nfse_response + "</p>", subject_data="Unable to generate nfse in " + lambda_constants["domain_name"], region=lambda_constants["region"])
