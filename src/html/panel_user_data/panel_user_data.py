from python_web_frame.panel_page import PanelPage
from python_web_frame.user_page import UserPage
from utils.utils.Http import Http
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Validation import Validation
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.JsonData import JsonData
from utils.utils.StrFormat import StrFormat
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Ses import Ses
from objects.User import load_user
import time


class PanelUserData(PanelPage, UserPage):
    name = "Painel - Perfil do Usuário"
    public = False
    bypass = False
    admin = False

    def render_get(self):
        if self.path.get("render_props") == "False":
            self.render_props = False

        html = super().parse_html()

        html.esc("user_name_val", self.user.user_name)
        html.esc("user_email_val", self.user.user_email)
        html.esc("user_country_val", self.user.user_address_data["user_country"])

        user_country_alpha_2 = self.user.user_address_data["user_country"]
        html.esc("user_country_alpha_2_lower_val", user_country_alpha_2.lower())
        html.esc("html_user_country_options", self.list_html_user_country_options(user_country_alpha_2))
        html.esc("user_country_code_val", JsonData().get_country_phone_code()[self.user.user_address_data["user_country"]])
        html.esc("user_phone_val", self.user.user_phone)

        if self.user.user_client_type == "physical":
            html.esc("physical_active_val", "active")
            html.esc("physical_address_div_visibility_val", "")
            html.esc("physical_address_submit_div_visibility_val", "")
            html.esc("company_address_div_visibility_val", "display:none;")
            html.esc("company_address_submit_div_visibility_val", "display:none;")
            html.esc("international_address_div_visibility_val", "display:none;")
            html.esc("international_address_submit_div_visibility_val", "display:none;")
            html.esc("client_type_spans_div_visibility_val", "")

        if self.user.user_client_type == "company":
            html.esc("company_active_val", "active")
            html.esc("physical_address_div_visibility_val", "display:none;")
            html.esc("physical_address_submit_div_visibility_val", "display:none;")
            html.esc("company_address_div_visibility_val", "")
            html.esc("company_address_submit_div_visibility_val", "")
            html.esc("international_address_div_visibility_val", "display:none;")
            html.esc("international_address_submit_div_visibility_val", "display:none;")
            html.esc("client_type_spans_div_visibility_val", "")

        if self.user.user_client_type == "international":
            html.esc("physical_address_div_visibility_val", "display:none;")
            html.esc("physical_address_submit_div_visibility_val", "display:none;")
            html.esc("company_address_div_visibility_val", "display:none;")
            html.esc("company_address_submit_div_visibility_val", "display:none;")
            html.esc("international_address_div_visibility_val", "")
            html.esc("international_address_submit_div_visibility_val", "")
            html.esc("client_type_spans_div_visibility_val", "display:none;")

        html.esc("user_cpf_val", self.user.user_cpf)
        html.esc("user_cnpj_val", self.user.user_cnpj)
        html.esc("user_zip_code_val", self.user.user_address_data["user_zip_code"])
        html.esc("user_state_val", self.user.user_address_data["user_state"])
        html.esc("user_city_val", self.user.user_address_data["user_city"])
        html.esc("user_city_code_val", self.user.user_address_data["user_city_code"])
        html.esc("user_neighborhood_val", self.user.user_address_data["user_neighborhood"])
        html.esc("user_street_val", self.user.user_address_data["user_street"])
        html.esc("user_street_number_val", self.user.user_address_data["user_street_number"])
        html.esc("user_complement_val", self.user.user_address_data["user_complement"])

        html.esc("user_thumb_url_val", self.user.generate_user_thumb_url())
        html.esc("user_thumb_val", self.user.user_thumb)

        html.esc("html_delete_account_modal", str(ReadWrite().read_html("panel_user_data/_codes/html_delete_account_modal")))
        html.esc("html_delete_thumb_modal", str(ReadWrite().read_html("panel_user_data/_codes/html_delete_thumb_modal")))
        html.esc("html_loader_modal_searching_address", str(ReadWrite().read_html("panel_user_data/_codes/html_loader_modal_searching_address")))
        html.esc("html_loader_modal_delete_account", str(ReadWrite().read_html("panel_user_data/_codes/html_loader_modal_delete_account")))
        html.esc("html_loader_modal_process_uploaded_image", str(ReadWrite().read_html("panel_user_data/_codes/html_loader_modal_process_uploaded_image")))

        if self.render_props:
            html.esc("my_plan_main_class_val", "my-plan__main")

        if not self.render_props:
            html.esc("render_props_visibility_val", "display:none;")

        return str(html)
        # self.check_error_msg(html, self.error_msg)
        # if self.user.user_client_type != self.path["user_client_type"]:
        #     self.user.clear_perdonal_data()

        # if self.render_props:
        #     html.esc("my_plan_main_class_val", "my-plan__main")
        #     html.esc("user_thumb_url_val", self.user.generate_user_thumb_url())
        #     # html.esc("html_modify_cookies_configuration", ReadWrite().read_html("panel_user_data/_codes/html_modify_cookies_configuration"))
        #     html.esc("html_delete_account_modal", ReadWrite().read_html("panel_user_data/_codes/html_delete_account_modal"))
        #     html.esc("html_loader_modal", ReadWrite().read_html("panel_user_data/_codes/html_loader_modal"))

        # else:
        #     html.esc("panel_user_data_modal_visibility_val", "none")

        # if self.path["user_client_type"] == "physical":
        #     html.esc("html_physical_or_company_form", self.show_html_physical_form())

        # elif self.path["user_client_type"] == "company":
        #     html.esc("html_physical_or_company_form", self.show_html_company_form())

        # elif self.path["user_client_type"] == "international":
        #     html.esc("html_physical_or_company_form", self.show_html_international_form())

        # html.esc("html_modal_loader_spinner", self.show_html_modal_loader_spinner())
        # return str(html)

    def render_post(self):
        return self.render_get()
        if not self.path.get("user_client_type"):
            return ReadWrite().redirect("checkout_order_summary")
        if self.path.get("render_props") == "False":
            self.render_props = False

        if not self.post.get("user_email"):
            return self.render_get_with_error("Por favor informe um email.")
        user_changed_email = False
        if self.post["user_email"] != self.user.user_email:
            check_user = load_user(self.post["user_email"])
            if check_user:
                return self.render_get_with_error("Já existe um usuário com este email cadastrado.")
            user_changed_email = True

        if self.path["user_client_type"] == "physical":
            if not self.post.get("user_name"):
                return self.render_get_with_error("Por favor informe um nome.")
            if self.post.get("user_phone"):
                if not Validation().check_if_br_phone(self.post["user_phone"]):
                    return self.render_get_with_error("Por favor informe um número de telefone válido.")
            if self.post.get("user_cpf"):
                if not Validation().check_if_cpf(self.post["user_cpf"]):
                    return self.render_get_with_error("Por favor informe um número CPF válido.")
            if self.post.get("user_zip_code"):
                if self.post.get("user_street_number"):
                    if self.post["user_street_number"] == "0":
                        return self.render_get_with_error("Por favor informe um número de endereço válido.")

                api_cep_response = Http().get_request_address_data_with_zip_code(self.post["user_zip_code"])
                if not api_cep_response:
                    return self.render_get_with_error("O código postal informado é inválido.")

                self.post["user_state"] = api_cep_response["state"]
                self.post["user_city"] = api_cep_response["city"]
                self.post["user_city_code"] = api_cep_response["city_code"]
                self.post["user_neighborhood"] = api_cep_response["neighborhood"]
                self.post["user_street"] = api_cep_response["street"]

        if self.path["user_client_type"] == "company":
            if not self.post.get("user_cnpj"):
                return self.render_get_with_error("Por favor informe um CNPJ.")
            if not Validation().check_if_cnpj(self.post["user_cnpj"]):
                return self.render_get_with_error("Por favor informe um número CNPJ válido.")

            if not self.post.get("user_name"):
                return self.render_get_with_error("Por favor informe um nome.")
            if self.post.get("user_phone"):
                if not Validation().check_if_br_phone(self.post["user_phone"]):
                    return self.render_get_with_error("Por favor informe um número de telefone válido.")

            api_cnpj_response = Http().get_request_cnpj_address_data(self.post["user_cnpj"])
            if not api_cnpj_response:
                return self.render_get_with_error("Nenhum dado encontrado para o CNPJ informado.")

            self.post["user_name"] = api_cnpj_response["name"]
            self.post["user_zip_code"] = api_cnpj_response["zip_code"]
            self.post["user_state"] = api_cnpj_response["state"]
            self.post["user_city"] = api_cnpj_response["city"]
            self.post["user_neighborhood"] = api_cnpj_response["neighborhood"]
            self.post["user_street"] = api_cnpj_response["street"]
            self.post["user_state_number"] = api_cnpj_response["street_number"]
            if api_cnpj_response.get("complement"):
                self.post["user_complement"] = api_cnpj_response["complement"]

        if self.path["user_client_type"] == "international":
            if not self.post.get("user_name"):
                return self.render_get_with_error("Por favor informe um nome.")

            if self.post.get("user_phone"):
                if not Validation().check_if_phone(self.post["user_phone"], self.post["user_country"]):
                    return self.render_get_with_error("Por favor informe um número de telefone válido.")

        self.user.user_name = self.post["user_name"]
        self.user.user_first_three_letters_name = self.user.user_name[:3]
        self.user.user_phone = self.post.get("user_phone", "")
        self.user.user_cpf = self.post.get("user_cpf", "")
        self.user.user_cnpj = self.post.get("user_cnpj", "")
        self.user.user_client_type = self.path["user_client_type"]

        self.user.user_address_data["user_country"] = self.post.get("user_country", "BR").upper()
        self.user.user_address_data["user_zip_code"] = self.post.get("user_zip_code", "").lower()
        self.user.user_address_data["user_state"] = self.post.get("user_state", "").lower()
        self.user.user_address_data["user_city"] = self.post.get("user_city", "").lower()
        self.user.user_address_data["user_city_code"] = self.post.get("user_city_code", "").lower()
        self.user.user_address_data["user_neighborhood"] = self.post.get("user_neighborhood", "").lower()
        self.user.user_address_data["user_street"] = self.post.get("user_street", "").lower()
        self.user.user_address_data["user_street_number"] = self.post.get("user_street_number", "").lower()
        self.user.user_address_data["user_complement"] = self.post.get("user_complement", "").lower()
        self.user.user_aggre_with_communication = bool(self.post.get("user_aggre_with_communication"))

        self.user.update_cart_currency()
        self.user.check_if_payment_ready()
        self.user.update_attribute("user_address_data_last_update", str(time.time()))
        Dynamo().put_entity(self.user.__dict__)

        if not self.render_props:
            if not self.user.user_payment_ready:
                return self.render_get_with_error("Perfil atualizado porém é necessário preencher todos os campos para processeguir com a compra")

        if user_changed_email:
            self.user.update_auth_token()
            self.send_email_modified_email(self.user.user_email, self.user.user_auth_token, self.post["user_email"])
            return self.render_get_with_error("Perfil atualizado porém para alterar o seu email é necessário seguir as instruções que acabamos de enviar para o seu email atual")

        return self.render_get_with_error("Perfil atualizado com sucesso")
