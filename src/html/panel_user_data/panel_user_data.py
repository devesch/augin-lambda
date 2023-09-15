from python_web_frame.panel_page import PanelPage
from utils.utils.Http import Http
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Validation import Validation
from utils.utils.JsonData import JsonData
from utils.utils.StrFormat import StrFormat
from utils.AWS.Dynamo import Dynamo


class PanelUserData(PanelPage):
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
        if self.user.user_client_type != self.path["user_client_type"]:
            self.user.clear_perdonal_data()

        if self.render_props:
            html.esc("html_paneluserdata_div", ReadWrite().read_html("panel_user_data/_codes/html_paneluserdata_div"))
            html.esc("html_paneluserdata_div", ReadWrite().read_html("panel_user_data/_codes/html_paneluserdata_div"))
            html.esc("html_paneluserbox_div", ReadWrite().read_html("panel_user_data/_codes/html_paneluserbox_div"))
            html.esc("html_change_password_link", ReadWrite().read_html("panel_user_data/_codes/html_change_password_link"))
            html.esc("html_modify_cookies_configuration", ReadWrite().read_html("panel_user_data/_codes/html_modify_cookies_configuration"))
            html.esc("html_close_div", ReadWrite().read_html("panel_user_data/_codes/html_close_div"))

        if self.path["user_client_type"] == "physical":
            html.esc("html_physical_or_company_form", self.show_html_physical_form())

        elif self.path["user_client_type"] == "company":
            html.esc("html_physical_or_company_form", self.show_html_company_form())

        elif self.path["user_client_type"] == "international":
            html.esc("html_physical_or_company_form", self.show_html_international_form())

        return str(html)

    def render_post(self):
        if not self.path.get("user_client_type"):
            return ReadWrite().redirect("checkout_order_summary")
        if self.path.get("render_props") == "False":
            self.render_props = False

        if self.path["user_client_type"] == "physical":
            # TODO: como vai ficar a tradução aqui nessas mensagens hardcoded?
            if not self.post.get("user_name"):
                return self.render_get_with_error("Por favor informe um nome.")
            if not self.post.get("user_phone"):
                return self.render_get_with_error("Por favor informe um número de telefone.")
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
            # TODO: como vai ficar a tradução aqui nessas mensagens hardcoded?
            if not self.post.get("user_cnpj"):
                return self.render_get_with_error("Por favor informe um CNPJ.")
            if not Validation().check_if_cnpj(self.post["user_cnpj"]):
                return self.render_get_with_error("Por favor informe um número CNPJ válido.")

            if not self.post.get("user_name"):
                return self.render_get_with_error("Por favor informe um nome.")
            if not self.post.get("user_phone"):
                return self.render_get_with_error("Por favor informe um número de telefone.")
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

            if not self.post.get("user_phone"):
                return self.render_get_with_error("Por favor informe um número de telefone.")
            if not ReadWrite().validate_phone(self.post["user_phone"], self.post["user_country"]):
                return self.render_get_with_error("Por favor informe um número de telefone válido.")

        self.user.user_name = self.post["user_name"]
        self.user.user_first_three_letters_name = self.user.user_name[:3]
        self.user.user_phone = self.post["user_phone"]
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

        if self.post.get("user_aggre_with_communication"):
            self.user.user_aggre_with_communication = True
        else:
            self.user.user_aggre_with_communication = False

        self.user.update_cart_currency()
        self.user.check_if_is_payment_ready()
        Dynamo().put_entity(self.user.__dict__)

        if not self.render_props:
            if not self.user.user_payment_ready:
                return self.render_get_with_error("Perfil atualizado porém é necessário preencher todos os campos para processeguir com a compra")
        return self.render_get_with_error("Perfil atualizado com sucesso.")

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

        if not self.user.user_address_data["user_zip_code"]:
            html.esc("box_inputs_style_val", "display:none;")

        if not self.render_props:
            html.esc("html_onclick_change_to_company_form", str(ReadWrite().read_html("panel_user_data/_codes/html_onclick_change_to_company_form")))
            html.esc("html_onsubmit_physical_form", str(ReadWrite().read_html("panel_user_data/_codes/html_onsubmit_physical_form")))

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

        if not self.user.user_address_data["user_zip_code"]:
            html.esc("box_inputs_style_val", "display:none;")

        if not self.render_props:
            html.esc("html_onclick_change_to_physical_form", str(ReadWrite().read_html("panel_user_data/_codes/html_onclick_change_to_physical_form")))
            html.esc("html_onsubmit_company_form", str(ReadWrite().read_html("panel_user_data/_codes/html_onsubmit_company_form")))

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

        html.esc("html_user_country_options", self.list_html_user_country_options(user_country_alpha_2))
        html.esc("html_user_phone_input", self.generate_html_user_phone_input(user_country_alpha_2, self.user.user_phone))

        if self.post.get("user_phone"):
            html.esc("user_phone_val", ReadWrite().format_to_phone(self.post["user_phone"]))
        else:
            html.esc("user_phone_val", ReadWrite().format_to_phone(self.user.user_phone))

        if self.post.get("user_cpf"):
            html.esc("user_cpf_val", ReadWrite().format_to_cpf(self.post["user_cpf"]))
        elif hasattr(self.user, "user_cpf"):
            html.esc("user_cpf_val", ReadWrite().format_to_cpf(self.user.user_cpf))
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

        return str(html)

    def generate_html_user_phone_input(self, user_country_alpha_2, user_phone=""):
        html = ReadWrite().read_html("user_register/_codes/html_user_phone_input")
        html.esc("user_country_alpha_2_lower_val", user_country_alpha_2.lower())
        html.esc("user_country_code_val", JsonData().get_country_phone_code()[user_country_alpha_2])
        if user_country_alpha_2.upper() == "BR":
            html.esc("html_oninput_maskToPhone", str(ReadWrite().read_html("user_register/_codes/html_oninput_mask_to_phone")))
            html.esc("user_phone_input_maxlength_val", "15")
            if self.post.get("user_phone"):
                html.esc("user_phone_val", StrFormat().format_to_phone(self.post["user_phone"]))
            if user_phone:
                html.esc("user_phone_val", StrFormat().format_to_phone(user_phone))
        elif user_country_alpha_2.upper() != "BR":
            html.esc("user_phone_input_maxlength_val", "17")
            if self.post.get("user_phone"):
                html.esc("user_phone_val", self.post["user_phone"])
            if user_phone:
                html.esc("user_phone_val", user_phone)
        return str(html)
