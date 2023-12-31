from distutils.dir_util import copy_tree
from os import makedirs, path, walk, system, getcwd, remove
import shutil
from distutils.dir_util import copy_tree
from os import path, makedirs, getcwd
from boto3 import client
import shutil
from boto3 import client
from time import time


lambda_constants = {"region": "us-east-1"}
lambda_client = client("lambda", lambda_constants["region"])
root_folder = getcwd().replace("\\", "/") + "/"
upload_project_folder = root_folder.replace((root_folder.split("/")[-2] + "/"), "") + "build_" + str(root_folder.split("/")[-2])


def make_dirs_and_copy(upload_project_folder, dest_folder):
    if not path.exists(upload_project_folder):
        makedirs(upload_project_folder)
    if not path.exists(dest_folder):
        makedirs(dest_folder)
    for dirs in root_dirs:
        copy_tree(root_folder + dirs, dest_folder + dirs, preserve_mode=1, preserve_times=1, update=0, verbose=1, dry_run=0)


print("Running UPDATE lambda_check_model_uploaded_file")
root_dirs = ["utils", "python_web_frame", "objects"]
dest_folder = upload_project_folder + "/lambda_check_model_uploaded_file_tmp/"
make_dirs_and_copy(upload_project_folder, dest_folder)
shutil.copy(root_folder + "lambda_check_model_uploaded_file.py", dest_folder + "lambda_function.py")
shutil.make_archive(upload_project_folder + "/archive", "zip", dest_folder)
f = open(upload_project_folder + "/archive.zip", "rb")
response = lambda_client.update_function_code(FunctionName="check_model_uploaded_file", ZipFile=f.read())
print(str(response))


print("Running UPDATE lambda_periodic_actions")
root_dirs = ["utils"]
dest_folder = upload_project_folder + "/lambda_periodic_actions_tmp/"
make_dirs_and_copy(upload_project_folder, dest_folder)
shutil.copy(root_folder + "lambda_periodic_actions.py", dest_folder + "lambda_function.py")
shutil.make_archive(upload_project_folder + "/archive", "zip", dest_folder)
f = open(upload_project_folder + "/archive.zip", "rb")
response = lambda_client.update_function_code(FunctionName="periodic_actions", ZipFile=f.read())
print(str(response))


print("Running UPDATE lambda_move_deleted_model_files")
root_dirs = ["utils"]
dest_folder = upload_project_folder + "/lambda_move_deleted_model_files_zip_tmp/"
make_dirs_and_copy(upload_project_folder, dest_folder)
shutil.copy(root_folder + "lambda_move_deleted_model_files.py", dest_folder + "lambda_function.py")
shutil.make_archive(upload_project_folder + "/archive", "zip", dest_folder)
f = open(upload_project_folder + "/archive.zip", "rb")
response = lambda_client.update_function_code(FunctionName="move_deleted_model_files", ZipFile=f.read())
print(str(response))


print("Running UPDATE lambda_generate_folder_zip")
root_dirs = ["utils"]
dest_folder = upload_project_folder + "/lambda_generate_folder_zip_tmp/"
make_dirs_and_copy(upload_project_folder, dest_folder)
shutil.copy(root_folder + "lambda_generate_folder_zip.py", dest_folder + "lambda_function.py")
shutil.make_archive(upload_project_folder + "/archive", "zip", dest_folder)
f = open(upload_project_folder + "/archive.zip", "rb")
response = lambda_client.update_function_code(FunctionName="generate_folder_zip", ZipFile=f.read())
print(str(response))


print("Running UPDATE lambda_EC2-Launcher")
root_dirs = []
dest_folder = upload_project_folder + "/lambda_EC2-Launcher_tmpass/"
make_dirs_and_copy(upload_project_folder, dest_folder)
shutil.copy(root_folder + "lambda_EC2-Launcher.py", dest_folder + "lambda_function.py")
shutil.make_archive(upload_project_folder + "/archive", "zip", dest_folder)
f = open(upload_project_folder + "/archive.zip", "rb")
response = lambda_client.update_function_code(FunctionName="EC2-Launcher", ZipFile=f.read())
print(str(response))


print("Running UPDATE lambda_process_xml_to_dynamo")
root_dirs = ["utils/", "objects/"]
dest_folder = upload_project_folder + "/process_xml_to_dynamo_tmp/"
make_dirs_and_copy(upload_project_folder, dest_folder)
shutil.copy(root_folder + "lambda_process_xml_to_dynamo.py", dest_folder + "lambda_function.py")
shutil.make_archive(upload_project_folder + "/archive", "zip", dest_folder)
f = open(upload_project_folder + "/archive.zip", "rb")
response = lambda_client.update_function_code(FunctionName="process_xml_to_dynamo", ZipFile=f.read())
print(str(response))

print("Running UPDATE lambda_web_data_process_json")
root_dirs = ["utils"]
upload_project_folder = root_folder.replace((root_folder.split("/")[-2] + "/"), "") + "build_" + str(root_folder.split("/")[-2])
dest_folder = upload_project_folder + "/web-data-process-json_tmp/"
make_dirs_and_copy(upload_project_folder, dest_folder)
shutil.copy(root_folder + "lambda_web_data_process_json.py", dest_folder + "lambda_function.py")
shutil.make_archive(upload_project_folder + "/archive", "zip", dest_folder)
f = open(upload_project_folder + "/archive.zip", "rb")
response = lambda_client.update_function_code(FunctionName="web-data-process-json", ZipFile=f.read())
print(str(response))


print("Running UPDATE lambda_generate_pdf")
root_dirs = ["pdfkit/", "utils"]
dest_folder = upload_project_folder + "/lambda_generate_pdf_tmp/"
make_dirs_and_copy(upload_project_folder, dest_folder)
shutil.copy(root_folder + "lambda_generate_pdf.py", dest_folder + "lambda_function.py")
shutil.make_archive(upload_project_folder + "/archive", "zip", dest_folder)
f = open(upload_project_folder + "/archive.zip", "rb")
response = lambda_client.update_function_code(FunctionName="lambda_generate_pdf", ZipFile=f.read())
print(str(response))
