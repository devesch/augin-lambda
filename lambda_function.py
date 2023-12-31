import json
import os
import importlib

from utils.Event import Event
from objects.User import load_user
from utils.AWS.Dynamo import Dynamo
from utils.AWS.Ses import Ses
from utils.Code import Code
from utils.Config import Config, lambda_constants
from utils.utils.Http import Http
from utils.utils.EncodeDecode import EncodeDecode
from utils.utils.StrFormat import StrFormat
from python_web_frame.verify_path import get_path_data

available_routes = os.listdir("src/html")
available_routes.append("api")


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as e:
        event = Event(event)
        Ses().send_error_email(event, lambda_constants["domain_name"] + str(event.get_prefix()) + " pages lambda", e)

        lang = event.get_lang() or "pt"
        page = "error"

        importlib.import_module("src.html." + page + "." + page)
        class_instance = getattr(getattr(importlib.import_module("src.html." + page), page), StrFormat().format_snakecase_to_camelcase(page))()

        set_instance_attributes(class_instance, event, page, None, None, None, lang, user=None, project_cookies=None, error_msg=None)
        return Http().respond(getattr(class_instance, "render_get")(), event, status_code=201)


def set_instance_attributes(class_instance, event, page, cookie_policy, path, post, lang, user, project_cookies, error_msg):
    setattr(class_instance, "route", page)
    setattr(class_instance, "cookie_policy", cookie_policy)
    setattr(class_instance, "event", event)
    setattr(class_instance, "path", path)
    setattr(class_instance, "post", post)
    setattr(class_instance, "error_msg", error_msg)
    setattr(class_instance, "user", user)
    setattr(class_instance, "project_cookies", project_cookies)
    setattr(class_instance, "lang", lang)


def initialize_user(event):
    user = load_user(event.get_user_auth_token())
    if user:
        user.update_last_login_at()
    return user


def initialize_api_class_instance(event):
    api_class = event.get_second_param_in_raw_path()
    importlib.import_module(f"api.{api_class}")
    return getattr(getattr(importlib.import_module("api"), api_class), StrFormat().format_snakecase_to_camelcase(api_class))()


def initialize_page_class_instance(page):
    importlib.import_module("src.html." + page + "." + page)
    class_instance = getattr(getattr(importlib.import_module("src.html." + page), page), StrFormat().format_snakecase_to_camelcase(page))()
    return class_instance


def main_lambda_handler(event, context):
    event = Event(event)
    method, page = event.get_method(), event.get_first_param_in_raw_path()
    print(json.dumps(method) + " -> " + str(page) + " -> " + str(event))

    if method not in ("get", "post"):
        return Http().respond("", event, status_code=405)
    if page not in available_routes:
        return Http().respond("", event, status_code=405)

    post = Http().format_post_data(event.get_post_data())
    # Config().update_lambda_contants(event.get_prefix(), post)
    # Dynamo().update_dynamo_constants()
    user = initialize_user(event)
    lang = event.get_lang() or "pt"
    cookie_policy = event.get_cookie_policy() or None
    lambda_constants["current_language"] = lang
    path = get_path_data(event.get_path(), user)
    project_cookies = event.get_project_cookies()

    if page == "robots.txt":
        return Http().text_response("User-agent: *\nDisallow:\nAllow: /home")

    if page == "api":
        class_instance = initialize_api_class_instance(event)
        set_instance_attributes(class_instance, event, page, cookie_policy, path, post, lang, user, project_cookies, path.get("error_msg"))
        response = getattr(class_instance, "run")()
        response["event"] = str(event)
        if response.get("success"):
            if type(response["success"]) == str:
                if response["success"] in Code().get_translations():
                    response["success"] = Code().get_translations()[response["success"]][lang]
        if response.get("error"):
            if type(response["error"]) == str:
                if response["error"] in Code().get_translations():
                    response["error"] = Code().get_translations()[response["error"]][lang]
        return Http().json_response(response)
    else:
        if "error" in path:
            page = "error"
        class_instance = initialize_page_class_instance(page)
        if user and class_instance.bypass:
            return Http().respond(Http().redirect("panel_your_plan"), event)
        if not user and not class_instance.public:
            return Http().respond(Http().redirect(f"user_login/?error_msg={EncodeDecode().encode_to_url('Você precisa estar logado para acessar esta página')}"), event)
        if user and user.user_credential != "admin" and class_instance.admin and page not in ("backoffice_login_as_another_user", "backoffice_order_nfse_pdf"):
            return Http().respond(Http().redirect(f"user_login/?error_msg={EncodeDecode().encode_to_url('Você não possui as credenciais para acessar esta página')}"), event)
        set_instance_attributes(class_instance, event, page, cookie_policy, path, post, lang, user, project_cookies, path.get("error_msg"))
        response = getattr(class_instance, f"render_{method}")()
        return Http().respond(response, event, user)


import os

if os.environ.get("AWS_EXECUTION_ENV") is None and not os.getenv("LOCAL_SERVER"):
    with open("_testnow.json", "r") as read_file:
        html = main_lambda_handler(json.load(read_file), None)
        print("END")
