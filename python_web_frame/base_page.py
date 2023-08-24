from objects.User import User
from utils.Code import Code
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Generate import Generate
from utils.utils.StrFormat import StrFormat
from utils.AWS.Dynamo import Dynamo


class BasePage:
    name = ""
    public = False
    bypass = False
    admin = False
    render_props = True
    route = ""
    event = None
    path = {}
    post = {}
    backoffice_data = None
    dynamo = None
    utils = None
    error_msg = ""
    lang = None
    user = None
    update_user_cookie = False
    project_cookies = None

    def translate(self, translate_key):
        return Code().get_translations()[translate_key][self.lang]

    def parse_html(self, common_changes={}):
        common_changes["page_title"] = StrFormat().format_snakecase_to_title(self.route)
        html = ReadWrite().read_html(self.route + "/index", common_changes)
        if self.render_props:
            if "header" in html.placeholders:
                html.esc("header", self.render_header(common_changes))
            if "menu_panel_no_icons" in html.placeholders:
                html.esc("menu_panel_no_icons", self.render_menu_panel_no_icons(common_changes))
            if "menu" in html.placeholders:
                html.esc("menu", self.render_menu(common_changes))
            if "footer" in html.placeholders:
                html.esc("footer", self.render_footer(common_changes))
        if "user_url_val" in html.placeholders:
            html.esc("user_url_val", self.event.get_url())
        return html

    def render_header(self, common_changes={}):
        html = ReadWrite().read_html("main/header", common_changes)
        font_format = Generate().generate_font_from_user_agent(self.event.get_user_agent())
        html.esc("font_ext_val", font_format)
        html.esc("font_type_val", font_format)
        html.esc("page_title_val", self.name)
        return str(html)

    def render_menu_panel_no_icons(self, common_changes={}):
        html = ReadWrite().read_html("main/menu_panel_no_icons", common_changes)
        return str(html)

    def render_footer(self, common_changes={}):
        html = ReadWrite().read_html("main/footer", common_changes)
        return str(html)

    def render_get_with_error(self, error_msg):
        self.error_msg = error_msg
        return self.render_get()

    def load_user(self, user_email):
        user = User(user_email)
        user.load_information()
        if user.user_status == "not_created":
            user = None
        return user

    def check_error_msg(self, html, error_msg=""):
        if error_msg:
            if error_msg in Code().get_translations():
                html.esc("error_msg_val", self.translate(error_msg))
            else:
                html.esc("error_msg_val", error_msg)
            if "sucesso" in error_msg:
                html.esc("error_msg_visibility_val", "color:#0FA958;")
            else:
                html.esc("error_msg_visibility_val", "color:#FF0000;")
        else:
            html.esc("error_msg_visibility_val", "display:none;")

    def increase_backoffice_data_total_count(self, entity):
        backoffice_data = self.get_backoffice_data()
        entity_keys = {"order": "backoffice_data_total_order_count", "user": "backoffice_data_total_user_count", "model": "backoffice_data_total_model_count"}
        if entity in entity_keys:
            key = entity_keys[entity]
            if key not in backoffice_data:
                backoffice_data[key] = "0"
            backoffice_data[key] = str(int(backoffice_data[key]) + 1)
            Dynamo().update_entity(backoffice_data, key, backoffice_data[key])

    def get_backoffice_data(self):
        backoffice_data = Dynamo().get_backoffice_data()
        if not backoffice_data:
            from objects.BackofficeData import BackofficeData

            backoffice_data = BackofficeData()
            backoffice_data = backoffice_data.__dict__
            Dynamo().put_entity(backoffice_data)
        return backoffice_data
