from python_web_frame.base_page import BasePage
from utils.utils.JsonData import JsonData
from utils.Config import lambda_constants


class PanelUserDataChangeCountry(BasePage):
    def run(self):
        if not self.post.get("selected_country"):
            return {"error": "no selected_country found in post"}
        if not self.post.get("user_client_type"):
            return {"error": "no user_client_type found in post"}
        if self.post["selected_country"] not in JsonData().get_country_data():
            return {"error": "invalid selected_country found in post"}
        if self.post["selected_country"] == "BR" and self.post["user_client_type"] == "international":
            return {"success": lambda_constants["domain_name_url"] + "/panel_user_data/?user_client_type=physical"}
        if self.post["selected_country"] != "BR" and self.post["user_client_type"] != "international":
            return {"success": lambda_constants["domain_name_url"] + "/panel_user_data/?user_client_type=international&selected_country=" + self.post["selected_country"]}
        return {"error": "Nenhuma mudança de URL necessária"}
