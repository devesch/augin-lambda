from python_web_frame.base_page import BasePage
from utils.utils.Http import Http


class PanelGetAddressDataWithZip(BasePage):
    def run(self):
        # self.utils.send_payload_email(self.event, "CEP DATA")
        if not self.post.get("user_zip_code"):
            return {"error": "Nenhum código postal fornecido"}
        api_cep_response = Http().get_request_address_data_with_zip_code(self.post["user_zip_code"])
        if not api_cep_response:
            return {"error": "Código postal inválido"}
        return {"success": api_cep_response}
