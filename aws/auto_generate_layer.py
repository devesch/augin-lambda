import os.path
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import time
import os
from win32com import client

### DELETE ALL DOCKER CONTAINERS AND IMAGES, BEFORE INPUT THE CONTAINER ID OPEN DOCKER DESKTOP AND CLICK "START" ON IMAGE, THEN COPY CONTAINER ID

python_libs = "signxml numpy cryptography dynamodb-encryption-sdk phonenumbers Pillow python-dateutil qrcode requests user-agents sl-zerobounce suds stripe"
# python_libs = "signxml"

# function = "augin"
# layer_name = "default"
# python_libs = "pandas openpyxl xlsxwriter"
# python_libs = "Pillow pillow-avif-plugin"


class ActivateVenv:
    def send_command(self, shell, command):
        """runs the command script"""

        shell.SendKeys(command + "{ENTER}")

    def open_cmd(self, shell):
        """opens cmd"""

        shell.run("cmd.exe")
        time.sleep(1)


# with open("aws/Dockerfile_with_six") as read_file:
#     docker_code = read_file.read()

with open("aws/Dockerfile") as read_file:
    docker_code = read_file.read()
docker_code = docker_code.replace("python_libs_val", python_libs)
docker_file = open("aws/docker/Dockerfile", "w")
docker_file.write(docker_code)
docker_file.close()

shell = client.Dispatch("WScript.Shell")
run_venv = ActivateVenv()
run_venv.open_cmd(shell)
run_venv.send_command(shell, "cd aws")
run_venv.send_command(shell, "cd docker")
run_venv.send_command(shell, "docker build -t amzlinuxpy39 . --no-cache")

docker_id = input("type docker id: ")
# docker_id =
# run_venv.send_command(shell, "docker cp 11ff31643bd99312dc7d5527663c93440499ee3dc05a569b7a6106c56e0d9da4:/docker_layer.zip ./")

run_venv.open_cmd(shell)
run_venv.send_command(shell, "cd aws")
run_venv.send_command(shell, "cd docker")
run_venv.send_command(shell, "docker cp " + docker_id + ":/docker_layer.zip ./")

# s3_client.upload_file("aws\docker\docker_layer.zip", lambda_constants["cdn_bucket"], "docker_layer.zip")

# publish_layer_version_response = lambda_client.publish_layer_version(LayerName=layer_name, Description=layer_name, Content={"S3Bucket": lambda_constants["cdn_bucket"], "S3Key": "docker_layer.zip"}, CompatibleRuntimes=["python3.9"], LicenseInfo="default", CompatibleArchitectures=["x86_64", "arm64"])
# update_function_configuration_response = lambda_client.update_function_configuration(FunctionName=function, Layers=[publish_layer_version_response["LayerVersionArn"]])

# s3_client.delete_objects(Bucket=lambda_constants["cdn_bucket"], Delete={"Objects": [{"Key": "docker_layer.zip"}]})


print("end")
