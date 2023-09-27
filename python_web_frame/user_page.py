from python_web_frame.base_page import BasePage
from objects.VerifyEmail import VerifyEmail
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Ses import Ses
from utils.utils.ReadWrite import ReadWrite
from utils.utils.JsonData import JsonData
from utils.utils.Sort import Sort
from utils.utils.StrFormat import StrFormat
from utils.utils.EncodeDecode import EncodeDecode


class UserPage(BasePage):
    def __init__(self) -> None:
        super().__init__()

    def list_html_user_country_options(self, user_country):
        full_html = []
        language_countries = JsonData().get_country_data()
        for country_alpha_2, country in language_countries.items():
            language_countries[country_alpha_2]["translated_name"] = self.translate(country["name"])
        language_countries = Sort().sort_dict_by_attribute_in_key(language_countries, "translated_name", integer=False)
        for country_alpha_2, country in language_countries.items():
            html = ReadWrite().read_html("user_register/_codes/html_user_country_options")
            html.esc("country_alpha_2_val", country_alpha_2)
            html.esc("country_name_val", country["translated_name"])
            if country_alpha_2 == user_country.upper():
                html.esc("pre_sel_val", 'selected=""')
            full_html.append(str(html))
        return "".join(full_html)

    def generate_and_send_email_verification_code(self):
        verify_email_code = self.generate_random_verify_code()
        verify_email = VerifyEmail(user_email=self.post["user_email"], verify_email_code=verify_email_code)
        Dynamo().put_entity(verify_email.__dict__)
        self.send_verify_email(self.post["user_email"], verify_email_code)

    def generate_random_verify_code(self):
        import random

        code = ""
        for x in range(6):
            code += str(random.randint(1, 9))
        return code

    def send_verify_email(self, user_email, verify_email_code):
        html = ReadWrite().read_html("user_verify_email/_codes/html_verify_email")
        html.esc("verify_email_code_val", verify_email_code)
        html.esc("user_encoded_email_val", EncodeDecode().encode_to_b64(user_email))
        
        Ses().send_email(user_email, body_html=str(html), body_text=str(html), subject_data="Augin - Seu código de verficação é " + verify_email_code)
        return

    def generate_verification_code(self):
        verification_code = ""
        for index in range(1, 7):
            if self.post.get("verify_email_code_" + str(index)):
                verification_code += self.post["verify_email_code_" + str(index)]
        if len(verification_code) == 6:
            return verification_code
        return None

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
