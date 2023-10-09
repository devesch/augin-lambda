from python_web_frame.backoffice_page import BackofficePage
from python_web_frame.controllers.billing_controller import BillingController
import xml.etree.ElementTree as ET
from utils.Config import lambda_constants
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Date import Date
from utils.utils.Http import Http
from utils.utils.StrFormat import StrFormat


class BackofficeOrderNfsePdf(BackofficePage):
    name = "Backoffice - Ordens NFSE"
    public = True
    bypass = False
    admin = False

    def render_get(self):
        html = super().parse_html()
        nfse_user = self.load_user(self.path["order"]["order_user_id"])
        if self.path["order"]["order_currency"] == "brl":
            html.esc("html_brl_or_international_nfse_pdf", self.show_html_brl_nfse_pdf(nfse_user))
        elif self.path["order"]["order_currency"] == "usd":
            html.esc("html_brl_or_international_nfse_pdf", self.show_html_international_nfse_pdf(nfse_user))
        return str(html)

    def render_post(self):
        return self.render_get()

    def show_html_international_nfse_pdf(self, nfse_user):
        html = ReadWrite().read_html("backoffice_order_nfse_pdf/_codes/html_international_nfse_pdf")
        if self.path["order"]["order_status"] == "refunded":
            html.esc("html_international_nfse_canceled", ReadWrite().read_html("backoffice_order_nfse_pdf/_codes/html_international_nfse_canceled"))
        html.esc("order_id_val", self.path["order_id"])
        html.esc("order_date_val", Date().format_unixtime(self.path["order"]["created_at"], "%d/%m/%y"))
        html.esc("nfse_user_name_val", nfse_user.user_name)
        html.esc("nfse_user_address_val", nfse_user.user_address_data["user_neighborhood"])
        html.esc("nfse_user_city_val", nfse_user.user_address_data["user_city"])
        html.esc("nfse_user_zip_code_val", nfse_user.user_address_data["user_zip_code"])
        html.esc("nfse_user_country_val", nfse_user.user_address_data["user_country"])
        html.esc("order_commentary_val", self.path["order"]["order_descrimination"].split("\n ")[0])
        html.esc("order_brl_price_val", StrFormat().format_to_money(self.path["order"]["order_brl_price"], "brl"))
        return str(html)

    def show_html_brl_nfse_pdf(self, nfse_user):
        html = ReadWrite().read_html("backoffice_order_nfse_pdf/_codes/html_brl_nfse_pdf")
        nfse_xml = BillingController().get_bill_of_sale_xml(self.path["order"])
        xml_tree = ET.ElementTree(nfse_xml)
        xml_tree.write(lambda_constants["tmp_path"] + "xml_tree.xml")
        nfse_json = self.convert_xml_into_json(ReadWrite().read_file(lambda_constants["tmp_path"] + "xml_tree.xml"))
        if "NfseCancelamento" in ReadWrite().read_file(lambda_constants["tmp_path"] + "xml_tree.xml"):
            html.esc("html_brl_nfse_canceled", ReadWrite().read_html("backoffice_order_nfse_pdf/_codes/html_brl_nfse_canceled"))
        html.esc("nfse_year_val", nfse_json["Numero"][:-11])
        html.esc("nfse_number_val", int(nfse_json["Numero"][4:]))
        html.esc("nfse_date_val", nfse_json["DataEmissao"].split("T")[0].replace("-", "/"))
        html.esc("nfse_time_val", nfse_json["DataEmissao"].split("T")[1].replace("-", "/"))
        html.esc("nfse_competency_val", nfse_json["Competencia"].split("T")[0].replace("-", "/"))
        html.esc("nfse_verification_code_val", nfse_json["CodigoVerificacao"])
        html.esc("company_name_val", lambda_constants["company_name"])
        html.esc("company_cnpj_val", lambda_constants["cnpj"])
        html.esc("company_municipal_inscription_val", lambda_constants["municipal_inscription"])
        if nfse_json.get("Cpf"):
            html.esc("nfse_cpf_val", StrFormat().format_to_cpf(nfse_json["Cpf"]))
        elif nfse_json.get("Cnpj_2"):
            html.esc("nfse_cnpj_val", StrFormat().format_to_cnpj(nfse_json["Cnpj_2"]))
        html.esc("nfse_social_reason_val", nfse_json["RazaoSocial_2"])
        api_cep_response = Http().get_request_address_data_with_zip_code(nfse_json["Cep_2"])
        if api_cep_response:
            html.esc("nfse_address_val", api_cep_response.get("street").title())
            html.esc("nfse_address_number_val", nfse_json["Numero_4"])
            html.esc("nfse_district_val", api_cep_response.get("neighborhood").title())
            html.esc("nfse_city_val", api_cep_response.get("city").title())
            html.esc("nfse_state_val", api_cep_response.get("state").upper())
        else:
            if nfse_user.get("user_address_data"):
                if "user_street" in nfse_user.get("user_address_data") and "user_street_number" in nfse_user.get("user_address_data") and "user_neighborhood" in nfse_user.get("user_address_data") and "user_city" in nfse_user.get("user_address_data") and "user_state" in nfse_user.get("user_address_data"):
                    html.esc("nfse_address_val", nfse_user.user_address_data["user_street"].title())
                    html.esc("nfse_address_number_val", nfse_user.user_address_data["user_street_number"])
                    html.esc("nfse_district_val", nfse_user.user_address_data["user_neighborhood"].title())
                    html.esc("nfse_city_val", nfse_user.user_address_data["user_city"].title())
                    html.esc("nfse_state_val", nfse_user.user_address_data["user_state"].upper())
        html.esc("nfse_address_val", "NÃO INFORMADO")
        html.esc("nfse_address_number_val", "S/N")
        html.esc("nfse_district_val", "NÃO INFORMADO")
        html.esc("nfse_city_val", "PORTO ALEGRE")
        html.esc("nfse_state_val", "RS")

        html.esc("user_email_val", nfse_user.user_email)

        if nfse_user.user_phone:
            html.esc("user_phone_val", StrFormat().format_to_phone(nfse_user.user_phone))
        else:
            html.esc("user_phone_val", "NÃO INFORMADO")

        html.esc("nfse_descrimination_val", nfse_json["Discriminacao"].replace("\n ", "<br><br>"))
        html.esc("nfse_service_list_val", nfse_json["ItemListaServico"])
        html.esc("nfse_service_value_val", nfse_json["ValorServicos"])
        html.esc("nfse_aliq_val", int(float(nfse_json["Aliquota"]) * 100))
        html.esc("nfse_iss_val", StrFormat().format_to_money(nfse_json["ValorIss"], "brl"))
        if nfse_json.get("CodigoCancelamento"):
            html.esc("html_canceled_nfse", self.show_html_canceled_nfse())
        return str(html)

    def show_html_canceled_nfse(self):
        html = ReadWrite().read_html("backoffice_order_nfse_pdf/_codes/html_brl_nfse_canceled")
        return str(html)

    def convert_xml_into_json(self, xml_string):
        json = {}
        tags = xml_string.split("<ns")
        for tag in tags:
            if "<" in tag:
                if tag.split(":")[1].split(">")[0] not in json:
                    json[tag.split(":")[1].split(">")[0]] = tag.split(">")[1].split("<")[0]
                elif tag.split(":")[1].split(">")[0] + "_2" not in json:
                    json[tag.split(":")[1].split(">")[0] + "_2"] = tag.split(">")[1].split("<")[0]
                elif tag.split(":")[1].split(">")[0] + "_3" not in json:
                    json[tag.split(":")[1].split(">")[0] + "_3"] = tag.split(">")[1].split("<")[0]
                elif tag.split(":")[1].split(">")[0] + "_4" not in json:
                    json[tag.split(":")[1].split(">")[0] + "_4"] = tag.split(">")[1].split("<")[0]
                elif tag.split(":")[1].split(">")[0] + "_5" not in json:
                    json[tag.split(":")[1].split(">")[0] + "_5"] = tag.split(">")[1].split("<")[0]
        return json
