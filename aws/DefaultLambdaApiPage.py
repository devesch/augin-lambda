from python_web_frame.base_page import BasePage


class default_api_page_name_val(BasePage):
    def run(self):
        if not self:
            return {"error": ""}
        return {"success": ""}
