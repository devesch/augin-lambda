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

    def render_menu(self, common_changes={}):
        if self.route == "webview" and not self.user:
            html = ReadWrite().read_html("main/menu_no_icons", common_changes)
            html.esc("webview_class_val", "webview-header")
            return str(html)
        else:
            html = ReadWrite().read_html("main/menu", common_changes)

        if self.route == "webview":
            html.esc("webview_class_val", "webview-header")

        if self.user:
            html.esc("has_user_input_val", "True")
            html.esc("user_name_val", self.user.user_name)
            if not self.user.user_is_tqs:
                html.esc("user_company_val", "Augin")
                html.esc("user_email_val", self.user.user_email)
            else:
                html.esc("user_company_val", self.user.user_tqs_company)
                html.esc("user_email_val", self.user.user_tqs_email)
                if self.user.user_tqs_customers:
                    html.esc("html_projects_customers_options", self.list_projects_customers_options(self.user.user_tqs_customers))
        else:
            html.esc("has_user_input_val", "False")
        html.esc(self.route + "_active_val", "active")
        if self.route == "projects":
            html.esc("my_projects_active_val", "active")
        if self.route == "projects_customer":
            html.esc("projects_active_val", "active")

        models_in_processing = Dynamo().query_user_models_from_state(self.user, "in_processing")
        if models_in_processing:
            html.esc("in_processing_projects_amount_val", str(len(models_in_processing)))
        else:
            html.esc("in_processing_projects_style_val", "display:none;")

        models_waiting_for_data = Dynamo().query_user_models_from_state(self.user, "waiting_for_data")
        if models_waiting_for_data:
            html.esc("pending_projects_amount_val", str(len(models_waiting_for_data)))
        else:
            html.esc("pending_projects_style_val", "display:none;")
        return str(html)

    # def show_html_projects_customer_div(self, user_tqs_customers):
    #     html = ReadWrite().read_html("main/_codes/html_projects_customer_div")
    #     html.esc("html_projects_customers_options", self.list_projects_customers_options(user_tqs_customers))
    #     html.esc(self.route + "_active_val", "active")
    #     return str(html)

    def list_projects_customers_options(self, user_tqs_customers):
        full_html = []
        for customer in user_tqs_customers:
            html = ReadWrite().read_html("main/_codes/html_projects_customers_options")
            html.esc("customer_id_val", customer["id"])
            html.esc("customer_name_val", customer["name"])
            if self.path.get("customer_id") == customer["id"]:
                html.esc("active_val", "active")
            full_html.append(str(html))
        return "".join(full_html)

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
