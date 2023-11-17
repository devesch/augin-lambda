from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import os
import codecs
from flask import Flask, request, send_from_directory
import importlib
import lambda_function
import time
import subprocess
import signal
import sys
import random

app = Flask(__name__, static_folder="src/")


last_new_change = 0
new_change = 1
running_webpack = False
modified_files = set()
observer_thread = None
modified_thread = None


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

        if ".py" in event.src_path:
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
            os.system("npm run dev")


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

    # subprocess.run(["python", "tools_for_devs/create_translations.py"])
    context = {}

    importlib.reload(lambda_function)

    response = lambda_function.lambda_handler(event, context)
    from utils.Config import lambda_constants

    global last_new_change, new_change

    # if response["body"][:27] != "<script>function openPage()" and not "api/" in path and last_new_change != new_change:
    #     last_new_change = new_change
    #     os.system("npm run dev")

    with codecs.open("src/dist/style/style.css", "r", "utf-8-sig") as css:
        css = css.read()
    with codecs.open("src/dist/js/index.js", "r", "utf-8-sig") as js_index:
        js_index = js_index.read()

    return (
        response["body"],
        response["statusCode"],
        response["headers"] if "headers" in response else {},
    )


if __name__ == "__main__":
    if observer_thread is None or not observer_thread.is_alive():
        observer_thread = threading.Thread(target=start_observer, name="ObserverThread")
        observer_thread.start()

    if modified_thread is None or not modified_thread.is_alive():
        modified_thread = threading.Thread(target=start_modified, name="ModifiedThread")
        modified_thread.start()

    while True:
        try:
            app.run(debug=True, port=3000, use_reloader=False)
        except:
            continue


print("END")
