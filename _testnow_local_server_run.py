import json
import os
import subprocess
import time

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


def create_translations():
    try:
        subprocess.run(["python3.11", "create_translations.py"])
    except:
        subprocess.run(["python", "create_translations.py"])


def load_environment_variables():
    with open(".vscode/launch.json", "r", encoding="utf-8") as file:
        launch = json.load(file)

    os.environ["AWS_ACCESS_KEY_ID"] = launch["configurations"][0]["env"]["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = launch["configurations"][0]["env"]["AWS_SECRET_ACCESS_KEY"]
    os.environ["AWS_DEFAULT_REGION"] = launch["configurations"][0]["env"]["AWS_DEFAULT_REGION"]
    os.environ["LOCAL_SERVER"] = launch["configurations"][0]["env"]["AWS_DEFAULT_REGION"]


def run_subprocess():
    if "bernardo" in os.getcwd() or "/Users/devesch" in os.getcwd():
        create_translations()
        process = subprocess.Popen(["python3", "_testnow_local_server.py"], env=os.environ)
    else:
        create_translations()
        process = subprocess.Popen(["python", "_testnow_local_server.py"], env=os.environ)
    return process


class OnMyWatch:
    # Set the directory on watch
    watchDirectory = os.getcwd()

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


class Handler(PatternMatchingEventHandler):
    patterns = ["*.py", "*.html"]

    def __init__(self):
        super().__init__()
        load_environment_variables()
        self.process = run_subprocess()

    def on_any_event(self, event):
        if self.process:
            self.process.terminate()
            self.process.wait()
        load_environment_variables()
        self.process = run_subprocess()
        print(f"{event.src_path} has been changed. Restarting the server.")


if __name__ == "__main__":
    load_environment_variables()
    watch = OnMyWatch()
    watch.run()
