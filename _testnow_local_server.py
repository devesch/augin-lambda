import importlib
import json
import os
import signal
import threading
import time

from flask import Flask, request, send_from_directory
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import lambda_function
from utils.utils.ReadWrite import ReadWrite

app = Flask(__name__, static_folder="src/")


last_new_change = 0
new_change = 1
running_webpack = False
modified_files = set()
observer_thread = None
modified_thread = None


def clear_js_and_scss():
    ReadWrite().write_file("src/js/index.js", "")
    ReadWrite().write_file("src/style/style.scss", "")


def concatenate_js():
    main_js = ReadWrite().read_file("src/js/index_base.js")
    for sub_dirs in os.listdir("src/html/"):
        if sub_dirs[0] != ".":
            for file in os.listdir(os.path.join("src/html/", sub_dirs)):
                if file[0] != ".":
                    if ".js" in file:
                        main_js += ReadWrite().read_file(os.path.join("src/html/", sub_dirs + "/" + file))
    ReadWrite().write_file("src/js/index.js", main_js)


def concatenate_scss():
    main_scss = ReadWrite().read_file("src/style/style_base.scss")
    for sub_dirs in os.listdir("src/html/"):
        if sub_dirs[0] != ".":
            for file in os.listdir(os.path.join("src/html/", sub_dirs)):
                if file[0] != ".":
                    if ".scss" in file:
                        main_scss += "\n" + ReadWrite().read_file(os.path.join("src/html/", sub_dirs + "/" + file))
    ReadWrite().write_file("src/style/style.scss", main_scss)


def static_files(filename):
    return send_from_directory(app.static_folder, filename)


class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global running_webpack, new_change, last_new_change

        if ".json" in event.src_path or "node_modules" in event.src_path or "dist" in event.src_path or "pyc" in event.src_path or "_testnow" in event.src_path or ".git" in event.src_path or "bin" in event.src_path:
            return None

        if ".css" in event.src_path or ".scss" in event.src_path or ".js" in event.src_path:
            print(f"File changed: {event.src_path}")

            modified_files.add(event.src_path)

        if ".py" in event.src_path or ".json" in event.src_path or ".html" in event.src_path:
            global app

            os.kill(os.getpid(), signal.SIGINT)


def start_observer():
    filechange_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(filechange_handler, path="./", recursive=True)
    observer.start()
    observer.join()


def start_modified():
    global modified_files
    while True:
        time.sleep(1)
        if modified_files:
            modified_files = set()
            # concatenate_js()
            # concatenate_scss()
            os.system("npm run dev")
            # clear_js_and_scss()


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

    if path.startswith("static/"):
        return send_from_directory(app.static_folder, path[len("static/") :])

    with open("_testnow.json", "w", encoding="utf-8") as json_file:
        json.dump(event, json_file, sort_keys=True, ensure_ascii=False, indent=4)

    context = {}
    importlib.reload(lambda_function)
    response = lambda_function.lambda_handler(event, context)
    return (response["body"], response["statusCode"], response["headers"] if "headers" in response else {})


if __name__ == "__main__":
    if observer_thread is None or not observer_thread.is_alive():
        observer_thread = threading.Thread(target=start_observer, name="ObserverThread")
        observer_thread.start()

    if modified_thread is None or not modified_thread.is_alive():
        modified_thread = threading.Thread(target=start_modified, name="ModifiedThread")
        modified_thread.start()

    while True:
        try:
            # clear_js_and_scss()
            app.run(debug=True, port=3000, use_reloader=False)
        except:
            continue


print("END")
