from json import dumps, loads
from base64 import b64decode
from urllib.parse import parse_qs


class Event:
    def __init__(self, event_dict):
        for attribute in event_dict:
            setattr(self, attribute, event_dict[attribute])

    def __str__(self):
        return dumps(self.__dict__)

    def get_cookie_policy(self):
        if hasattr(self, "cookies"):
            for cookie in self.cookies:
                if "__Secure-cookie-policy" in cookie:
                    parsed_cookie = parse_qs(cookie)
                    if parsed_cookie:
                        return loads(parsed_cookie["__Secure-cookie-policy"][0].replace("'", '"'))
        return {}

    def get_referer(self):
        if hasattr(self, "headers"):
            if "referer" in self.headers:
                return self.headers["referer"]

    def get_lang(self):
        if hasattr(self, "cookies"):
            for cookie in self.cookies:
                if "__Secure-lang" in cookie:
                    if parse_qs(cookie):
                        return parse_qs(cookie)["__Secure-lang"][0]

    def check_if_has_debug(self):
        if hasattr(self, "cookies"):
            for cookie in self.cookies:
                if "debug" in cookie.lower():
                    return True
        return False

    def get_user_auth_token(self):
        if hasattr(self, "cookies"):
            for cookie in self.cookies:
                if "__Secure-token" in cookie:
                    if parse_qs(cookie):
                        return parse_qs(cookie)["__Secure-token"][0]
        if hasattr(self, "headers"):
            if "__secure-token" in self.headers:
                return self.headers["__secure-token"]
        return None

    def get_project_cookies(self):
        if hasattr(self, "cookies"):
            for cookie in self.cookies:
                if "__Secure-projects-cookies" in cookie:
                    if parse_qs(cookie):
                        return loads(parse_qs(cookie)["__Secure-projects-cookies"][0].replace("'", '"'))
        return {}

    def get_prefix(self):
        if hasattr(self, "headers"):
            if "host" in self.headers:
                return self.headers["host"].split(".")[0]

    def get_user_authorization(self):
        if hasattr(self, "headers"):
            if "authorization" in self.headers:
                return self.headers["authorization"]
        return None

    def get_post_data(self):
        post = {}
        if hasattr(self, "body"):
            if self.isBase64Encoded == True:
                parameters = parse_qs(str(b64decode(self.body).decode("utf-8")))
                for param in parameters:
                    if parameters[param][0].strip() and len(parameters[param][0].strip()) < 100000:
                        post[param] = parameters[param][0].strip()
                if not parameters:
                    try:
                        parameters = loads(b64decode(self.body).decode("utf-8"))
                        for param in parameters:
                            post[param] = parameters[param]
                    except:
                        pass
            else:
                try:
                    post = loads(self.body)
                except:
                    post = self.body
                return post
        return post

    def get_first_param_in_raw_path(self):
        if hasattr(self, "rawPath"):
            first_param = self.rawPath.split("/")[1]
            if first_param == "":
                return "user_login"
            return first_param
        return "user_login"

    def get_second_param_in_raw_path(self):
        if hasattr(self, "rawPath"):
            return self.rawPath.split("/")[2]

    def get_path(self):
        path = {}
        if hasattr(self, "queryStringParameters"):
            if self.queryStringParameters:
                for key, value in self.queryStringParameters.items():
                    path[key] = value
        return path

    def get_headers(self):
        return getattr(self, "headers", None)

    def get_user_ip(self):
        return self.headers.get("x-forwarded-for", None)

    def get_user_ua_mobile(self):
        return self.headers.get("sec-ch-ua-mobile", None)

    def get_user_ua_platform(self):
        return self.headers.get("sec-ch-ua-platform", None)

    def get_user_agent(self):
        return self.headers.get("user-agent", None)

    def get_domain_name(self):
        return self.requestContext.get("domainName", "")

    def get_method(self):
        return self.requestContext["http"].get("method", "").lower()

    def get_url(self):
        if hasattr(self, "queryStringParameters"):
            params = ""
            for index, param in enumerate(self.queryStringParameters):
                if index == 0:
                    if param != "error_msg":
                        params += "?" + param + "=" + self.queryStringParameters[param]
                else:
                    if param != "error_msg":
                        params += "&" + param + "=" + self.queryStringParameters[param]
            return self.get_first_param_in_raw_path() + "/" + params
        return self.get_first_param_in_raw_path()

    def check_if_is_mobile(self):
        try:
            if "windows" in self.headers["user-agent"].lower() or "mac" in self.headers["user-agent"].lower():
                return False
            return True
        except:
            return False

    def check_if_has_cookies(self):
        if hasattr(self, "cookies"):
            return True
        return False
