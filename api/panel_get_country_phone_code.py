from python_web_frame.base_page import BasePage
from utils.utils.JsonData import JsonData


class PanelGetCountryPhoneCode(BasePage):
    def run(self):
        if not self.post.get("user_country_alpha_2"):
            return {"error": "Nenhum país fornecido"}

        return {"success": JsonData().get_country_phone_code()[self.post["user_country_alpha_2"].upper()]}
