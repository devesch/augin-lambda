import json
from utils.Config import lambda_constants
from utils.utils.Validation import Validation
from utils.utils.StrFormat import StrFormat

last_post_event = None


class Http:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Http, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def request(self, method="GET", url="", headers={}, data={}, json_res=True):
        import requests

        response = requests.request(method.upper(), url, headers=headers, data=json.dumps(data))
        if json_res:
            return json.loads(response.text)
        return response.text

    def get_param_from_url(self, url, param):
        from urllib.parse import urlparse, parse_qs

        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return query_params.get(param, [None])[0]

    def download_file_from_url(self, url, file_path):
        import requests

        response = requests.get(url)
        response.raise_for_status()

        with open(file_path, "wb") as file:
            file.write(response.content)

    def api_caller(self, api_route, post_data, user_auth_token=""):
        return self.request("POST", lambda_constants["domain_name_url"] + "/api/" + api_route, headers={"__Secure-token": user_auth_token}, data=post_data, json_res=True)

    def get_request_ip_data(self, user_ip):
        return self.request("GET", "https://api.ipdata.co/" + user_ip + "?api-key=" + lambda_constants["ip_data_api_key"])

    def get_request_address_data(self, user_zip_code):
        api_cep_response = self.request("GET", "https://brasilapi.com.br/api/cep/v2/" + user_zip_code, headers={"Content-Type": "application/json; charset=utf-8"})
        return api_cep_response

    def get_request_address_data_with_zip_code(self, user_zip_code):
        cep_address_data = {}
        api_cep_response = self.request("GET", "https://payment.augin.app/postal_address/" + user_zip_code, headers={"Content-Type": "application/json; charset=utf-8"})
        if not "errors" in api_cep_response:
            if "city" in api_cep_response:
                if "code" in api_cep_response["city"]:
                    cep_address_data = {
                        "state": api_cep_response["state"],
                        "city": api_cep_response["city"]["name"],
                        "city_code": api_cep_response["city"]["code"],
                        "neighborhood": api_cep_response["district"],
                        "street": api_cep_response["streetSuffix"] + " " + api_cep_response["street"],
                    }
        return cep_address_data

    def get_request_cnpj_address_data(self, user_cnpj):
        cnpj_address_data = {}
        api_cnpj_response = self.request("GET", "https://checkout.augin.app/cnpj_data/" + user_cnpj, headers={"Content-Type": "application/json; charset=utf-8"})
        if "name" in api_cnpj_response:
            cnpj_address_data = {
                "name": api_cnpj_response["name"],
                "zip_code": api_cnpj_response["address"]["postalCode"].replace("-", ""),
                "state": api_cnpj_response["address"]["state"],
                "city": api_cnpj_response["address"]["city"]["name"],
                "city_code": api_cnpj_response["address"]["city"]["code"],
                "neighborhood": api_cnpj_response["address"]["district"],
                "street": api_cnpj_response["address"]["street"],
                "street_number": api_cnpj_response["address"]["number"],
            }
        if api_cnpj_response.get("complement"):
            cnpj_address_data["complement"] = api_cnpj_response["address"]["additionalInformation"]
        return cnpj_address_data

    def slugify(self, text):
        non_url_safe = ["<", ">", "*", "!", '"', "#", "$", "%", "&", "+", ",", "/", ":", ";", "=", "?", "@", "[", "\\", "]", "^", "`", "{", "|", "}", "~", "'", "(", ")"]
        replace_slug_chars = {"ç": "c", "ã": "a", "á": "a", "à": "a", "õ": "o", "ó": "o", "é": "e", "í": "i", "ú": "o"}
        text = text.lower()
        for old_char, new_char in replace_slug_chars.items():
            text = text.replace(old_char, new_char)
        translate_table = {ord(char): "" for char in non_url_safe}
        text = text.translate(translate_table)
        text = "-".join(text.split())
        return text

    def format_post_value_without_dangerous_character(self, value, dangerous_character):
        return value.replace(dangerous_character, "")

    def format_post_data(self, post):
        dangerous_characters = ["<", ">", "?", ";", "[", "\\", "]", "|"]
        format_to_number_fields = []
        format_to_letter_fields = ["user_name"]
        acceptable_json_fields = ["last_evaluated_key"]
        ignore_param = []
        if not post:
            return {}

        for param, value in post.items():
            if isinstance(value, str):
                if param not in ignore_param:
                    for dangerous_character in dangerous_characters:
                        if dangerous_character in value:
                            post[param] = self.format_post_value_without_dangerous_character(post[param], dangerous_character)
                        if param not in acceptable_json_fields:
                            if Validation().check_if_is_json(value):
                                post[param] = ""

        for param, value in post.items():
            if value == "on":
                post[param] = True
            elif value == "true":
                post[param] = True
            elif value == "false":
                post[param] = False
            elif param in format_to_number_fields:
                post[param] = StrFormat().format_to_numbers(value)
            elif param in format_to_letter_fields:
                post[param] = StrFormat().format_to_letters(value)
            if param == "user_email":
                post[param] = post[param].lower()
            if param == "model_filename_external":
                post[param] = post[param].replace('"', "").replace("'", "")
            if param == "model_name":
                post[param] = post[param].replace('"', "").replace("'", "")
            if isinstance(post[param], str):
                post[param] = post[param].strip()
        return post

    def redirect(self, url):
        if url == "home":
            url = ""
        return f"<script>function openPage() {{ window.location.replace('{lambda_constants['domain_name_url']}/{url}'); }} document.onload = openPage();</script>"

    def redirect_to_another_url(self, url):
        if url == "home":
            url = ""
        return f"<script>function openPage() {{ window.location.replace('{url}'); }} document.onload = openPage();</script>"

    def html_response(self, body):
        return {"statusCode": 200, "body": str(body), "headers": {"Content-Type": "text/html; charset=utf-8", "Access-Control-Allow-Origin": "*"}}

    def json_response(self, body):
        return {"statusCode": 200, "body": json.dumps(body), "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}}

    def respond(self, html, event, user=None, user_cookie=False, status_code=200):
        import re

        method = event.get_method()
        if method == "post":
            global last_post_event
            last_post_event = event.__dict__

        command, user_auth_token, user_lang = None, None, None
        if isinstance(html, dict):
            command = html.get("command")
            user_auth_token = html.get("user_auth_token")
            project_cookies = html.get("project_cookies")
            user_lang = html.get("user_lang")
            html = html.get("html")

        if not Validation().check_if_local_env():
            html = html.replace("local_js_index_val", "").replace("local_css_val", "")

        event_here_man = f"<div id='EVENT HERE MAN' style='display:none;'>{event}<br><br><br>{json.dumps(last_post_event)}</div>"

        ### TODO REMOVE BEFORE PROD
        body = html + event_here_man
        # if "dev" in event.get_prefix():
        #     body = html + event_here_man
        # else:
        #     if event.check_if_has_debug():
        #         body = html + event_here_man
        #     else:
        #         body = html

        response = {
            "statusCode": status_code,
            "body": body,
            "headers": {
                "Content-Type": "text/html; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "X-XSS-Protection": "1; mode=block",
                "strict-transport-security": "max-age=31536000; includeSubDomains; preload",
                "X-Frame-Options": "DENY",
                "Permissions-Policy": "microphone=()",
            },
        }

        response["body"] = re.sub(r">\s+<", "><", response["body"])
        response["body"] = re.sub(r"<!--.*?-->", "", response["body"], flags=re.DOTALL)

        if "dev" in event.get_prefix():
            domain = (lambda_constants["domain_name_url"]).replace("https://" + lambda_constants["prefix_name"], ".")
        else:
            # domain = (lambda_constants["domain_name_url"]).replace("https://" + lambda_constants["prefix_name"], ".")
            domain = "tqs.com.br"
        if user_cookie:
            response["headers"]["Set-Cookie"] = f"__Secure-token={user.user_auth_token}; Secure; domain={domain}; path=/; Max-Age=7776000;"
        if command == "login":
            response["headers"]["Set-Cookie"] = f"__Secure-token={user_auth_token}; Secure; domain={domain}; path=/; Max-Age=7776000;"
        elif command == "logout":
            response["headers"]["Set-Cookie"] = f"__Secure-token=; Secure; domain={domain}; path=/; Max-Age=-1;"
        elif command == "change_lang":
            response["headers"]["Set-Cookie"] = f"__Secure-lang={user_lang}; Secure; domain={domain}; path=/; Max-Age=7776000;"
        elif command == "set_project_cookies":
            response["headers"]["Set-Cookie"] = f"__Secure-projects-cookies={project_cookies}; Secure; domain={domain}; path=/; Max-Age=604800;".replace('"', "'")
        return response
