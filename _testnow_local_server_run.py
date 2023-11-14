import subprocess
import os
import json
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


def load_environment_variables():
    with open(".vscode/launch.json", "r", encoding="utf-8") as file:
        launch = file.read()

    with open(".vscode/enviroment_variables.json", "r", encoding="utf-8") as file:
        enviroment_variables = json.load(file)

    os.environ["AWS_ACCESS_KEY_ID"] = launch.split('"AWS_ACCESS_KEY_ID": ')[1].split(",")[0].replace('"', "")
    os.environ["AWS_SECRET_ACCESS_KEY"] = launch.split('"AWS_SECRET_ACCESS_KEY": ')[1].split(",")[0].replace('"', "")
    os.environ["AWS_DEFAULT_REGION"] = enviroment_variables["region"]
    os.environ["LOCAL_SERVER"] = enviroment_variables["region"]


def run_subprocess():
    file_to_run = "_testnow_local_server.py"
    process = subprocess.Popen(["python", file_to_run], env=os.environ)
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
    patterns = ["*.py"]

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
