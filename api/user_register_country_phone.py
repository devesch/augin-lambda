from python_web_frame.user_page import UserPage


class UserRegisterCountryPhone(UserPage):
    def run(self):
        if not self.post.get("selected_country"):
            return {"error": "Nenhum selected_country encontrado no post"}
        if self.user:
            html = self.generate_html_user_phone_input(self.post["selected_country"], self.user.user_phone)
        else:
            html = self.generate_html_user_phone_input(self.post["selected_country"])
        return {"success": str(html)}
