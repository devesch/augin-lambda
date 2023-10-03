from objects.User import User
from utils.Code import Code
from utils.utils.ReadWrite import ReadWrite
from utils.utils.Generate import Generate
from utils.utils.StrFormat import StrFormat
from utils.AWS.Dynamo import Dynamo
from utils.Config import lambda_constants


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
            if "menu_panel" in html.placeholders:
                html.esc("menu_panel", self.render_menu_panel(common_changes))
            if "menu_panel_no_icons" in html.placeholders:
                html.esc("menu_panel_no_icons", self.render_menu_panel_no_icons(common_changes))
            if "menu_backoffice" in html.placeholders:
                html.esc("menu_backoffice", self.render_backoffice_menu(common_changes))
            if "menu" in html.placeholders:
                html.esc("menu", self.render_menu(common_changes))
            if "footer" in html.placeholders:
                html.esc("footer", self.render_footer(common_changes))
        if "user_url_val" in html.placeholders:
            html.esc("user_url_val", self.event.get_url())
        if "html_dropdown_select_user_pagination" in html.placeholders:
            html.esc("html_dropdown_select_user_pagination", self.show_html_dropdown_select_user_pagination(self.user.user_pagination_count))
        return html

    def render_header(self, common_changes={}):
        html = ReadWrite().read_html("main/header", common_changes)
        font_format = Generate().generate_font_from_user_agent(self.event.get_user_agent())
        html.esc("font_ext_val", font_format)
        html.esc("font_type_val", font_format)
        html.esc("page_title_val", self.name)

        if self.cookie_policy is None:
            html.esc("open_modal_cookie_policy_val", "active")
        else:
            if not "backoffice" in self.route and self.cookie_policy.get("tawk") == "accepted":
                html.esc("html_tawk_code", self.render_html_tawk_code(common_changes))
            if self.cookie_policy.get("mouseflow") == "accepted":
                if not "backoffice" in self.route and not "home" in self.route and not "history" in self.route:
                    html.esc("html_mouse_flow_code", self.render_html_mouse_flow_code(common_changes))
        return str(html)

    def render_backoffice_menu(self, common_changes={}):
        html = ReadWrite().read_html("main/menu_backoffice", common_changes)
        html.esc(self.route + "_active_val", "active")
        html.esc("user_name_val", self.user.user_name)
        html.esc("user_email_val", self.user.user_email)
        html.esc("user_client_type_val", self.user.user_client_type)
        html.esc("user_url_val", self.event.get_url())
        return str(html)

    def render_menu_panel(self, common_changes={}):
        html = ReadWrite().read_html("main/menu_panel", common_changes)
        html.esc(self.route + "_active_val", "active")
        html.esc("user_name_val", self.user.user_name)
        html.esc("user_email_val", self.user.user_email)
        html.esc("user_client_type_val", self.user.user_client_type)
        html.esc("user_url_val", self.event.get_url())
        html.esc("user_thumb_val", self.user.generate_user_thumb_url())
        if not self.user.user_plan_id:
            trial_plans = Dynamo().query_trial_plans()
            if trial_plans:
                if trial_plans[-1]["plan_id"] not in self.user.user_used_trials:
                    html.esc("html_trial_plan_promo_thumb", self.show_html_trial_plan_promo_thumb(trial_plans[-1]))
        return str(html)

    def render_menu_panel_no_icons(self, common_changes={}):
        html = ReadWrite().read_html("main/menu_panel_no_icons", common_changes)
        html.esc(self.route + "_active_val", "active")
        html.esc("user_url_val", self.event.get_url())
        return str(html)

    def render_footer(self, common_changes={}):
        html = ReadWrite().read_html("main/footer", common_changes)
        if self.cookie_policy:
            if self.cookie_policy.get("tawk") == "accepted":
                html.esc("open_tawk_or_open_cookies_modal_val", "Tawk_API.toggle()")
        else:
            html.esc("open_modal_cookie_policy_val", "active")

        html.esc("open_tawk_or_open_cookies_modal_val", "js.index.openCookiesContainer()")
        html.esc("user_url_val", self.event.get_url())
        return str(html)

    def show_html_upgrade_button(self, user_plan):
        html = ""
        if user_plan["plan_id"] == lambda_constants["free_plan_id"] or user_plan["plan_is_trial"]:
            html = ReadWrite().read_html("panel_create_project/_codes/html_upgrade_button")
        return str(html)

    def render_get_with_error(self, error_msg):
        self.error_msg = error_msg
        return self.render_get()

    def load_user(self, user_email):
        if not "@" in user_email:
            user_email = Dynamo().get_user_email_with_id(user_email)
        if not user_email:
            return None
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

    def render_html_tawk_code(self, common_changes={}):
        html = ReadWrite().read_html("main/_codes/html_tawk_code", common_changes)
        tawk_api_code = "5c61ca4c7cf662208c950f53/default" if self.lang == "pt" else "5dae0f3fdf22d91339a04c3c/default"
        html.esc("tawk_api_val", tawk_api_code)
        if self.user:
            html.esc("tawk_user_name_val", self.user.user_name)
            html.esc("tawk_user_email_val", self.user.user_email)
        return str(html)

    def render_html_mouse_flow_code(self, common_changes={}):
        html = ReadWrite().read_html("main/_codes/html_mouse_flow_code", common_changes)
        return str(html)

    def show_html_trial_plan_promo_thumb(self, trial_plan):
        html = ReadWrite().read_html("main/_codes/html_trial_plan_promo_thumb")
        html.esc("plan_name_val", trial_plan["plan_name_" + self.lang].replace(" Trial", ""))
        html.esc("plan_trial_duration_in_days_val", trial_plan["plan_trial_duration_in_days"])
        return str(html)

    def show_html_dropdown_select_user_pagination(self, user_pagination_count):
        html = ReadWrite().read_html("main/_codes/html_dropdown_select_user_pagination")
        html.esc(user_pagination_count + "_presel_val", "selected='selected'")
        return str(html)
