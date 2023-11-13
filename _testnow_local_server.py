from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import os
import codecs
from flask import Flask, request
import importlib
import lambda_function
import time

app = Flask(__name__)

css = None
js_index = None


# def reload_css_js(path):
#     global css, js_index
#     if ".css" in path or ".scss" in path or ".js" in path or css is None or js_index is None:
#         os.system("npm run dev")


# class FileChangeHandler(FileSystemEventHandler):
#     def on_modified(self, event):
#         if ".json" in event.src_path or "dist" in event.src_path or "pyc" in event.src_path or "_testnow" in event.src_path or ".git" in event.src_path or "bin" in event.src_path:
#             return None

#         print(f"File changed: {event.src_path}")
#         reload_css_js(event.src_path)
#         if ".py" in event.src_path or ".html" in event.src_path:
#             importlib.reload(lambda_function)


# def start_observer():
#     filechange_handler = FileChangeHandler()
#     observer = Observer()
#     observer.schedule(filechange_handler, path="./", recursive=True)
#     observer.start()
#     # observer.join()


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def all_paths(path):
    print(f"Request Path: {path}")
    print(f"Request Method: {request.method}")
    print(f"Request Headers: {request.headers}")
    print(f"Request Body: {request.data}")
    headers_dict = dict(request.headers)
    headers_dict["user-agent"] = headers_dict["User-Agent"]
    event = {
        "version": "2.0",
        "routeKey": f"{request.method} /{path}",
        "rawPath": f"/{path}",
        "rawQueryString": request.query_string.decode("utf-8"),
        "cookies": dict(request.cookies),
        "headers": headers_dict,
        "queryStringParameters": dict(request.args),
        "requestContext": {
            "http": {
                "method": request.method,
                "path": f"/{path}",
                "protocol": "HTTP/1.1",
                "sourceIp": request.remote_addr,
                "user-agent": request.user_agent.string,
            },
        },
        "body": dict(request.form),
        "isBase64Encoded": False,
    }
    context = {}

    importlib.reload(lambda_function)
    response = lambda_function.main_lambda_handler(event, context)
    from utils.Config import lambda_constants

    os.system("npm run dev")
    with codecs.open("src/dist/style/style.css", "r", "utf-8-sig") as css:
        css = css.read()
    with codecs.open("src/dist/js/index.js", "r", "utf-8-sig") as js_index:
        js_index = js_index.read()

    replacements = {
        "local_js_index_val": f"<script> {js_index} </script>",
        "local_css_val": f"<style> {css} </style>",
    }
    links_to_remove = [
        f'<link rel="preload" href="{lambda_constants["cdn"]}/style/style.css" as="style">',
        f'<link rel="preload" href="{lambda_constants["cdn"]}/js/index.js" as="script">',
        f'<link defer rel="stylesheet" type="text/css" href="{lambda_constants["cdn"]}/style/style.css" />',
        f'<script defer src="{lambda_constants["cdn"]}/js/index.js"></script>',
    ]
    for key, value in replacements.items():
        response["body"] = response["body"].replace(key, value)
    for link in links_to_remove:
        response["body"] = response["body"].replace(link, "")

    return (
        response["body"],
        response["statusCode"],
        response["headers"] if "headers" in response else {},
    )


if __name__ == "__main__":
    # observer_thread = threading.Thread(target=start_observer)
    # observer_thread.start()
    app.run(debug=True, port=3000)


print("END")
