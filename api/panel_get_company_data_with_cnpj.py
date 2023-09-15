from python_web_frame.base_page import BasePage
from utils.utils.Http import Http


class PanelGetCompanyDataWithCnpj(BasePage):
    def run(self):
        if not self.post.get("user_cnpj"):
            return {"error": "Nenhum CNPJ enviado no formulário."}
        cnpj_address_response = Http().get_request_cnpj_address_data(self.post["user_cnpj"])
        if not cnpj_address_response:
            return {"error": "Não foi possível encontrar dados com o CNPJ informado."}
        return {"success": cnpj_address_response}
