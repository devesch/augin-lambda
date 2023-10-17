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

        if not self.path.get("user_client_type"):
            return Http().redirect("panel_user_data/?user_client_type=" + self.user.user_client_type)

        html = super().parse_html()
        self.check_error_msg(html, self.error_msg)
        if self.user.user_client_type != self.path["user_client_type"]:
            self.user.clear_perdonal_data()

        if self.render_props:
            html.esc("my_plan_main_class_val", "my-plan__main")
            html.esc("user_thumb_url_val", self.user.generate_user_thumb_url())
            html.esc("html_paneluserdata_div", ReadWrite().read_html("panel_user_data/_codes/html_paneluserdata_div"))
            html.esc("html_paneluserdata_div", ReadWrite().read_html("panel_user_data/_codes/html_paneluserdata_div"))
            html.esc("html_paneluserbox_div", ReadWrite().read_html("panel_user_data/_codes/html_paneluserbox_div"))
            html.esc("html_change_password_link", ReadWrite().read_html("panel_user_data/_codes/html_change_password_link"))
            ### TODO WHEN TIAGO LIBERATE COOKIE POLICY UNCOMMENT LINE BELOW
            # html.esc("html_modify_cookies_configuration", ReadWrite().read_html("panel_user_data/_codes/html_modify_cookies_configuration"))
            html.esc("html_close_div", ReadWrite().read_html("panel_user_data/_codes/html_close_div"))
            html.esc("html_delete_account_button", ReadWrite().read_html("panel_user_data/_codes/html_delete_account_button"))
            html.esc("html_delete_account_modal", ReadWrite().read_html("panel_user_data/_codes/html_delete_account_modal"))
            html.esc("html_loader_modal", ReadWrite().read_html("panel_user_data/_codes/html_loader_modal"))

        else:
            html.esc("panel_user_data_modal_visibility_val", "none")

        if self.path["user_client_type"] == "physical":
            html.esc("html_physical_or_company_form", self.show_html_physical_form())

        elif self.path["user_client_type"] == "company":
            html.esc("html_physical_or_company_form", self.show_html_company_form())

        elif self.path["user_client_type"] == "international":
            html.esc("html_physical_or_company_form", self.show_html_international_form())

        html.esc("html_modal_loader_spinner", self.show_html_modal_loader_spinner())
        return str(html)

    def render_post(self):
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
        self.user.check_if_is_payment_ready()
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

    def send_email_modified_email(self, user_email, user_auth_token, new_user_email):
        html = ReadWrite().read_html("main/emails/html_email_modified_email")
        html.esc("user_auth_token_val", user_auth_token)
        html.esc("user_email_val", user_email)
        html.esc("new_user_email_val", new_user_email)
        html.esc("new_user_email_encoded_val", EncodeDecode().encode_to_b64(new_user_email))
        Ses().send_email(new_user_email, body_html=str(html), body_text=str(html), subject_data=self.translate("Augin - Solicitação de troca de email"))
        return

    def show_html_physical_form(self):
        html = ReadWrite().read_html("panel_user_data/_codes/html_physical_form")
        self.check_error_msg(html, self.error_msg)

        html.esc("user_email_val", self.user.user_email)
        if self.post.get("user_name"):
            html.esc("user_name_val", self.post["user_name"].title())
        else:
            html.esc("user_name_val", self.user.user_name.title())

        if self.post.get("user_country"):
            user_country_alpha_2 = self.post["user_country"]
        elif self.user.user_address_data.get("user_country"):
            user_country_alpha_2 = self.user.user_address_data["user_country"]
        else:
            ip_data = Http().get_request_ip_data(self.event.get_user_ip())
            user_country_alpha_2 = ip_data["country_code"].upper()

        html.esc("user_country_alpha_2_lower_val", user_country_alpha_2.lower())
        html.esc("html_user_country_options", self.list_html_user_country_options(user_country_alpha_2))
        html.esc("html_user_phone_input", self.generate_html_user_phone_input(user_country_alpha_2, self.user.user_phone))

        if self.post.get("user_phone"):
            html.esc("user_phone_val", StrFormat().format_to_phone(self.post["user_phone"]))
        else:
            html.esc("user_phone_val", StrFormat().format_to_phone(self.user.user_phone))

        if self.post.get("user_cpf"):
            html.esc("user_cpf_val", StrFormat().format_to_cpf(self.post["user_cpf"]))
        elif hasattr(self.user, "user_cpf"):
            html.esc("user_cpf_val", StrFormat().format_to_cpf(self.user.user_cpf))
        if self.post.get("user_cnpj"):
            html.esc("user_cnpj_val", self.post["user_cnpj"])
        elif hasattr(self.user, "user_cnpj"):
            html.esc("user_cpf_val", self.user.user_cnpj)

        if self.post.get("user_zip_code"):
            html.esc("user_zip_code_val", StrFormat().format_to_zip_code(self.post["user_zip_code"]))
        elif self.user.user_address_data["user_zip_code"]:
            html.esc("user_zip_code_val", StrFormat().format_to_zip_code(self.user.user_address_data["user_zip_code"]))

        if self.post.get("user_state"):
            html.esc("user_state_val", self.post["user_state"].upper())
        elif self.user.user_address_data["user_state"]:
            html.esc("user_state_val", self.user.user_address_data["user_state"].upper())

        if self.post.get("user_city"):
            html.esc("user_city_val", self.post["user_city"].capitalize())
        elif self.user.user_address_data["user_city"]:
            html.esc("user_city_val", self.user.user_address_data["user_city"].capitalize())

        if self.post.get("user_city_code"):
            html.esc("user_city_code_val", self.post["user_city_code"])
        elif self.user.user_address_data["user_city"]:
            html.esc("user_city_code_val", self.user.user_address_data["user_city_code"])

        if self.post.get("user_neighborhood"):
            html.esc("user_neighborhood_val", self.post["user_neighborhood"].capitalize())
        elif self.user.user_address_data["user_neighborhood"]:
            html.esc("user_neighborhood_val", self.user.user_address_data["user_neighborhood"].capitalize())

        if self.post.get("user_street"):
            html.esc("user_street_val", self.post["user_street"].capitalize())
        elif self.user.user_address_data["user_street"]:
            html.esc("user_street_val", self.user.user_address_data["user_street"].capitalize())

        if self.post.get("user_street_number"):
            html.esc("user_street_number_val", self.post["user_street_number"])
        elif self.user.user_address_data["user_street_number"]:
            html.esc("user_street_number_val", self.user.user_address_data["user_street_number"])

        if self.post.get("user_complement"):
            html.esc("user_complement_val", self.post["user_complement"])
        elif self.user.user_address_data["user_complement"]:
            html.esc("user_complement_val", self.user.user_address_data["user_complement"])

        if self.post.get("user_aggre_with_communication"):
            html.esc("user_aggre_with_communication_checked_val", "checked='checked'")
        elif self.user.user_aggre_with_communication:
            html.esc("user_aggre_with_communication_checked_val", "checked='checked'")

        if not self.user.user_address_data["user_zip_code"] and not self.post.get("user_zip_code"):
            html.esc("box_inputs_style_val", "display:none;")

        if not self.render_props:
            html.esc("html_onclick_change_to_company_form", str(ReadWrite().read_html("panel_user_data/_codes/html_onclick_change_to_company_form")))
            html.esc("html_onsubmit_physical_form", str(ReadWrite().read_html("panel_user_data/_codes/html_onsubmit_physical_form")))
        else:
            html.esc("panel_user_data_close_modal_visibility_val", "none")

        return str(html)

    def show_html_company_form(self):
        html = ReadWrite().read_html("panel_user_data/_codes/html_company_form")

        self.check_error_msg(html, self.error_msg)
        html.esc("user_email_val", self.user.user_email)

        if self.post.get("user_name"):
            html.esc("user_name_val", self.post["user_name"].title())
        else:
            html.esc("user_name_val", self.user.user_name.title())

        if self.post.get("user_phone"):
            html.esc("user_phone_val", StrFormat().format_to_phone(self.post["user_phone"]))
        else:
            html.esc("user_phone_val", StrFormat().format_to_phone(self.user.user_phone))

        if self.post.get("user_cnpj"):
            html.esc("user_cnpj_val", StrFormat().format_to_cnpj(self.post["user_cnpj"]))
        elif hasattr(self.user, "user_cnpj"):
            html.esc("user_cnpj_val", StrFormat().format_to_cnpj(self.user.user_cnpj))
        if self.post.get("user_cnpj"):
            html.esc("user_cnpj_val", self.post["user_cnpj"])
        elif hasattr(self.user, "user_cnpj"):
            html.esc("user_cpf_val", self.user.user_cnpj)

        if self.post.get("user_zip_code"):
            html.esc("user_zip_code_val", StrFormat().format_to_zip_code(self.post["user_zip_code"]))
        elif self.user.user_address_data["user_zip_code"]:
            html.esc("user_zip_code_val", StrFormat().format_to_zip_code(self.user.user_address_data["user_zip_code"]))

        if self.post.get("user_state"):
            html.esc("user_state_val", self.post["user_state"].upper())
        elif self.user.user_address_data["user_state"]:
            html.esc("user_state_val", self.user.user_address_data["user_state"].upper())

        if self.post.get("user_city"):
            html.esc("user_city_val", self.post["user_city"].capitalize())
        elif self.user.user_address_data["user_city"]:
            html.esc("user_city_val", self.user.user_address_data["user_city"].capitalize())

        if self.post.get("user_city_code"):
            html.esc("user_city_code_val", self.post["user_city_code"])
        elif self.user.user_address_data["user_city"]:
            html.esc("user_city_code_val", self.user.user_address_data["user_city_code"])

        if self.post.get("user_neighborhood"):
            html.esc("user_neighborhood_val", self.post["user_neighborhood"].capitalize())
        elif self.user.user_address_data["user_neighborhood"]:
            html.esc("user_neighborhood_val", self.user.user_address_data["user_neighborhood"].capitalize())

        if self.post.get("user_street"):
            html.esc("user_street_val", self.post["user_street"].capitalize())
        elif self.user.user_address_data["user_street"]:
            html.esc("user_street_val", self.user.user_address_data["user_street"].capitalize())

        if self.post.get("user_street_number"):
            html.esc("user_street_number_val", self.post["user_street_number"])
        elif self.user.user_address_data["user_street_number"]:
            html.esc("user_street_number_val", self.user.user_address_data["user_street_number"])

        if self.post.get("user_complement"):
            html.esc("user_complement_val", self.post["user_complement"])
        elif self.user.user_address_data["user_complement"]:
            html.esc("user_complement_val", self.user.user_address_data["user_complement"])

        if self.post.get("user_aggre_with_communication"):
            html.esc("user_aggre_with_communication_checked_val", "checked='checked'")
        elif self.user.user_aggre_with_communication:
            html.esc("user_aggre_with_communication_checked_val", "checked='checked'")

        if not self.user.user_address_data["user_zip_code"] and not self.post.get("user_zip_code"):
            html.esc("box_inputs_style_val", "display:none;")

        if not self.render_props:
            html.esc("html_onclick_change_to_physical_form", str(ReadWrite().read_html("panel_user_data/_codes/html_onclick_change_to_physical_form")))
            html.esc("html_onsubmit_company_form", str(ReadWrite().read_html("panel_user_data/_codes/html_onsubmit_company_form")))
        else:
            html.esc("panel_user_data_close_modal_visibility_val", "none")

        return str(html)

    def show_html_international_form(self):
        html = ReadWrite().read_html("panel_user_data/_codes/html_international_form")
        self.check_error_msg(html, self.error_msg)

        html.esc("user_email_val", self.user.user_email)
        if self.post.get("user_name"):
            html.esc("user_name_val", self.post["user_name"].title())
        else:
            html.esc("user_name_val", self.user.user_name.title())

        if self.post.get("user_country"):
            user_country_alpha_2 = self.post["user_country"]
        elif self.path.get("selected_country"):
            user_country_alpha_2 = self.path["selected_country"]
        elif self.user.user_address_data.get("user_country"):
            user_country_alpha_2 = self.user.user_address_data["user_country"]
        else:
            ip_data = ReadWrite().get_request_ip_data(self.event.get_user_ip())
            user_country_alpha_2 = ip_data["country_code"].upper()

        html.esc("user_country_alpha_2_lower_val", user_country_alpha_2.lower())
        html.esc("html_user_country_options", self.list_html_user_country_options(user_country_alpha_2))
        html.esc("html_user_phone_input", self.generate_html_user_phone_input(user_country_alpha_2, self.user.user_phone))

        if self.post.get("user_phone"):
            html.esc("user_phone_val", StrFormat().format_to_phone(self.post["user_phone"]))
        else:
            html.esc("user_phone_val", StrFormat().format_to_phone(self.user.user_phone))

        if self.post.get("user_cpf"):
            html.esc("user_cpf_val", StrFormat().format_to_cpf(self.post["user_cpf"]))
        elif hasattr(self.user, "user_cpf"):
            html.esc("user_cpf_val", StrFormat().format_to_cpf(self.user.user_cpf))
        if self.post.get("user_cnpj"):
            html.esc("user_cnpj_val", self.post["user_cnpj"])
        elif hasattr(self.user, "user_cnpj"):
            html.esc("user_cpf_val", self.user.user_cnpj)

        if self.post.get("user_zip_code"):
            html.esc("user_zip_code_val", self.post["user_zip_code"])
        elif self.user.user_address_data["user_zip_code"]:
            html.esc("user_zip_code_val", self.user.user_address_data["user_zip_code"])

        if self.post.get("user_state"):
            html.esc("user_state_val", self.post["user_state"].upper())
        elif self.user.user_address_data["user_state"]:
            html.esc("user_state_val", self.user.user_address_data["user_state"].upper())

        if self.post.get("user_city"):
            html.esc("user_city_val", self.post["user_city"].capitalize())
        elif self.user.user_address_data["user_city"]:
            html.esc("user_city_val", self.user.user_address_data["user_city"].capitalize())

        if self.post.get("user_city_code"):
            html.esc("user_city_code_val", self.post["user_city_code"])
        elif self.user.user_address_data["user_city"]:
            html.esc("user_city_code_val", self.user.user_address_data["user_city_code"])

        if self.post.get("user_neighborhood"):
            html.esc("user_neighborhood_val", self.post["user_neighborhood"].capitalize())
        elif self.user.user_address_data["user_neighborhood"]:
            html.esc("user_neighborhood_val", self.user.user_address_data["user_neighborhood"].capitalize())

        if self.post.get("user_street"):
            html.esc("user_street_val", self.post["user_street"].capitalize())
        elif self.user.user_address_data["user_street"]:
            html.esc("user_street_val", self.user.user_address_data["user_street"].capitalize())

        if self.post.get("user_street_number"):
            html.esc("user_street_number_val", self.post["user_street_number"])
        elif self.user.user_address_data["user_street_number"]:
            html.esc("user_street_number_val", self.user.user_address_data["user_street_number"])

        if self.post.get("user_complement"):
            html.esc("user_complement_val", self.post["user_complement"])
        elif self.user.user_address_data["user_complement"]:
            html.esc("user_complement_val", self.user.user_address_data["user_complement"])

        if self.post.get("user_aggre_with_communication"):
            html.esc("user_aggre_with_communication_checked_val", "checked='checked'")
        elif self.user.user_aggre_with_communication:
            html.esc("user_aggre_with_communication_checked_val", "checked='checked'")

        if not self.render_props:
            html.esc("html_onsubmit_international_form", str(ReadWrite().read_html("panel_user_data/_codes/html_onsubmit_international_form")))
        else:
            html.esc("panel_user_data_close_modal_visibility_val", "none")

        return str(html)
