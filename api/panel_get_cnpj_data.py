from python_web_frame.panel_page import PanelPage
from utils.utils.Http import Http
from utils.Config import lambda_constants


class PanelGetCnpjData(PanelPage):
    def run(self):
        if not self.post.get("cnpj"):
            return {"error": "Nenhum cnpj informado no post"}
        response = Http().request("GET", "https://legalentity.api.nfe.io/v1/legalentities/basicInfo/" + self.post["cnpj"] + "?apikey=" + lambda_constants["legalentity_api_key"])
        if "errors" in response:
            return {"error": response["errors"][0]["message"]}
        return {"success": response}
