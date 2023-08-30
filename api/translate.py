from python_web_frame.base_page import BasePage


class Translate(BasePage):
    def run(self):
        return {"success": self.translate(self.post["key"])}
