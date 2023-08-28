from distutils.dir_util import copy_tree
from utils.Config import lambda_constants
from utils.utils.ReadWrite import ReadWrite
import subprocess
from os import makedirs, path, walk, system, getcwd, remove
import pathlib
import json
import shutil
from boto3 import client
import uuid
from time import time
import queue
import threading
import re
import htmlmin
import codecs


def run_threaded(func):
    thread = threading.Thread(target=func)
    thread.start()
    return thread


# Running translations
subprocess.run(["python", "tools_for_devs/create_translations.py"])


print("Running UPDATE LAMBDA")
root_folder = getcwd().replace("\\", "/") + "/"
last_update_data = json.load(open("last_update_data.json", "r", encoding="utf-8"))
clean_js_css = False


with open(".vscode/enviroment_variables.json", "r", encoding="utf-8") as read_file:
    env_var = json.load(read_file)
    domain_name = env_var["domain_name"]
    prefix_name = env_var["prefix_name"]
    sufix_name = env_var["sufix_name"]
    region = env_var["region"]

if not path.exists("src/dist"):
    ### WEBPACK.PROD.TEMPLATE ###
    package_json = {"name": domain_name.title(), "version": "1.0.0", "description": "Projeto " + domain_name.title(), "main": "index.js", "scripts": {"dev": "webpack --config webpack.prod.js"}, "author": "Devesch", "license": "ISC"}
    with open("package.json", "w") as json_file:
        json.dump(package_json, json_file)

    with open("aws/webpack.prod.template.js", "r") as read_file:
        webpack_prod_template = read_file.read()

    webpack_prod_template = webpack_prod_template.replace("project_main_name", domain_name + sufix_name)
    with open("webpack.prod.js", "w") as template:
        template.write(webpack_prod_template)

    system("npm run dev")


def check_webpack_changes(web_pack_change_queue):
    web_pack_change = False
    ### CHECKING WEBPACK CHANGES ###
    for filepath, subdirs, files in walk(root_folder + "src/js"):
        for name in files:
            if str(pathlib.PurePath(filepath, name)).replace("\\", "/").replace(root_folder, "") not in last_update_data:
                web_pack_change = True
            elif last_update_data[str(pathlib.PurePath(filepath, name)).replace("\\", "/").replace(root_folder, "")] != path.getmtime(pathlib.PurePath(filepath, name)):
                web_pack_change = True
            last_update_data[str(pathlib.PurePath(filepath, name)).replace("\\", "/").replace(root_folder, "")] = path.getmtime(pathlib.PurePath(filepath, name))

    for filepath, subdirs, files in walk(root_folder + "src/style"):
        for name in files:
            if str(pathlib.PurePath(filepath, name)).replace("\\", "/").replace(root_folder, "") not in last_update_data:
                web_pack_change = True
            elif last_update_data[str(pathlib.PurePath(filepath, name)).replace("\\", "/").replace(root_folder, "")] != path.getmtime(pathlib.PurePath(filepath, name)):
                web_pack_change = True
            last_update_data[str(pathlib.PurePath(filepath, name)).replace("\\", "/").replace(root_folder, "")] = path.getmtime(pathlib.PurePath(filepath, name))
    web_pack_change_queue.put(web_pack_change)


def check_assets_folder(assets_folder_change_queue):
    assets_change = False
    assets_folders = ["fonts", "icons", "images", "videos", "web_view"]
    for assets_folder in assets_folders:
        for filepath, subdirs, files in walk(root_folder + "src/assets/" + assets_folder):
            for name in files:
                if str(pathlib.PurePath(filepath, name)).replace("\\", "/").replace(root_folder, "") not in last_update_data:
                    assets_change = True
                elif last_update_data[str(pathlib.PurePath(filepath, name)).replace("\\", "/").replace(root_folder, "")] != path.getmtime(pathlib.PurePath(filepath, name)):
                    assets_change = True
                last_update_data[str(pathlib.PurePath(filepath, name)).replace("\\", "/").replace(root_folder, "")] = path.getmtime(pathlib.PurePath(filepath, name))
    assets_folder_change_queue.put(assets_change)


def update_header_file(new_version):
    with open("src/html/main/header.html", "r") as read_file:
        header = read_file.read()

    old_version = header.split("/style/style")
    old_version = old_version[1].split(".css")[0]
    if old_version:
        header = header.replace(old_version, "")
    header = header.replace("style.css", "style_" + new_version + ".css")
    header = header.replace("index.js", "index_" + new_version + ".js")
    header = header.replace("utils.js", "utils_" + new_version + ".js")

    with open("src/html/main/header.html", "w") as read_file:
        read_file.write(header)


def remove_spaces(text):
    # Remove spaces between HTML tags
    html_pattern = re.compile(r">\s+<")
    text = html_pattern.sub("><", text.strip())

    # Remove spaces between }} {{ tags
    template_pattern = re.compile(r"\}\}([\s\S]*?)\{\{")
    matches = template_pattern.findall(text)

    for match in matches:
        cleaned_match = re.sub(r"\s+", " ", match).strip()
        text = text.replace(match, cleaned_match)
    return text


def delete_folder_contents(s3_client, bucket_name, folder_prefix, new_version):
    # List all objects with the given folder_prefix
    objects_to_delete = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

    # Iterate through the objects and delete them
    for obj in objects_to_delete.get("Contents", []):
        if new_version not in obj["Key"]:
            s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])


def clean_json_in_folder(folder):
    for root, dirs, files in walk(folder):
        root = path.normpath(root)
        for file in files:
            # Check if the file is an HTML file
            if file == ".DS_Store":
                remove(path.join(root, file))
                continue

            if file.endswith(".json"):
                with codecs.open(path.join(root, file), "r", "utf-8-sig") as f:
                    content = json.load(f)
                minified_content = json.dumps(content, separators=(",", ":"))
                # Write the minified content to the output JSON file
                with codecs.open(path.join(root, file), "w") as f:
                    f.write(minified_content)


def clean_html_in_folder(folder):
    for root, dirs, files in walk(folder):
        root = path.normpath(root)
        for file in files:
            # Check if the file is an HTML file
            if file == ".DS_Store":
                remove(path.join(root, file))


def upload_lambda():
    root_dirs = ["utils/", "objects/", "src/html", "api/", "python_web_frame/"]
    upload_project_folder = root_folder.replace((root_folder.split("/")[-2] + "/"), "") + "build_" + str(root_folder.split("/")[-2])
    dest_folder = upload_project_folder + "/tmp_augin-lambda/"
    if not path.exists(upload_project_folder):
        makedirs(upload_project_folder)
    if not path.exists(dest_folder):
        makedirs(dest_folder)
    ReadWrite().delete_files_inside_a_folder(dest_folder)
    for dirs in root_dirs:
        copy_tree(root_folder + dirs, dest_folder + dirs, preserve_mode=1, preserve_times=1, update=0, verbose=1, dry_run=0)
    clean_html_in_folder(dest_folder + "src/html")
    clean_json_in_folder(dest_folder + "utils/")
    shutil.copy(root_folder + "lambda_function.py", dest_folder + "lambda_function.py")
    shutil.make_archive(upload_project_folder + "/archive", "zip", dest_folder)
    f = open(upload_project_folder + "/archive.zip", "rb")
    lambda_client = client("lambda", region_name=lambda_constants["region"])
    response = lambda_client.update_function_code(FunctionName="augin-lambda", ZipFile=f.read())
    print("MAIN LAMBDA " + str(response))


def start_s3_client(s3_client_queue):
    s3_client = client("s3", region_name=lambda_constants["region"])
    s3_client_queue.put(s3_client)


def upload_index(s3_client, new_version):
    s3_client.upload_file("src/dist/js/index.js", lambda_constants["cdn_bucket"], "js/index_" + new_version + ".js", ExtraArgs={"ContentType": "text/javascript"})


def upload_utils(s3_client, new_version):
    s3_client.upload_file("src/dist/js/utils.js", lambda_constants["cdn_bucket"], "js/utils_" + new_version + ".js", ExtraArgs={"ContentType": "text/javascript"})


def upload_style(s3_client, new_version):
    s3_client.upload_file("src/dist/style/style.css", lambda_constants["cdn_bucket"], "style/style_" + new_version + ".css", ExtraArgs={"ContentType": "text/css"})


def get_files_to_exclude(data):
    newest_files = {}

    for date, filename in data:
        parts = filename.split("/")[1].split("_", maxsplit=1)
        if len(parts) > 1:
            prefix = parts[0]
            if prefix in newest_files:
                if date > newest_files[prefix][0]:
                    newest_files[prefix] = (date, filename)
            else:
                newest_files[prefix] = (date, filename)

    files_to_exclude = []

    for prefix, (date, latest_file) in newest_files.items():
        prefix_files = [filename for date, filename in data if filename.split("/")[1].startswith(prefix + "_") and filename != latest_file]
        if prefix_files:
            files_to_exclude.extend(prefix_files)

    return files_to_exclude


def get_files_in_s3_folder(s3_client, bucket, folder, queue):
    files_dates = []
    files = []
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=folder + "/")

    if "Contents" in response:
        for content in response["Contents"]:
            files_dates.append((content["LastModified"], content["Key"]))
    else:
        print("The folder" + folder + "is empty.")

    files = get_files_to_exclude(files_dates)
    queue.put(files)


def delete_files_in_s3(s3_client, bucket, files):
    delete_keys = {"Objects": []}
    for content in files:
        delete_keys["Objects"].append({"Key": content})
    s3_client.delete_objects(Bucket=bucket, Delete=delete_keys)


def create_invalidation(cloudfront_client, distribution_id):
    response = cloudfront_client.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            "Paths": {
                "Quantity": 1,
                "Items": [
                    "/*",
                ],
            },
            "CallerReference": str(uuid.uuid4()),
        },
    )
    return


def run():
    assets_change = False
    web_pack_change = False
    update_all_lambdas = False

    new_version = str(uuid.uuid4())
    print(f"New Version: {new_version}")
    update_header_file(new_version)

    web_pack_change_queue = queue.Queue()
    assets_folder_change_queue = queue.Queue()

    s3_client = client("s3", region_name=lambda_constants["region"])

    check_webpack_changes_thread = run_threaded(lambda: check_webpack_changes(web_pack_change_queue))
    check_assets_folder_change_thread = run_threaded(lambda: check_assets_folder(assets_folder_change_queue))
    check_webpack_changes_thread.join()
    check_assets_folder_change_thread.join()

    assets_change = assets_folder_change_queue.get()
    web_pack_change = web_pack_change_queue.get()

    if web_pack_change:
        system("npm run prod")

    upload_index_thread = run_threaded(lambda: upload_index(s3_client, new_version))
    upload_utils_thread = run_threaded(lambda: upload_utils(s3_client, new_version))
    upload_style_thread = run_threaded(lambda: upload_style(s3_client, new_version))

    upload_index_thread.join()
    upload_utils_thread.join()
    upload_style_thread.join()

    update_lambda_thread = run_threaded(lambda: upload_lambda())

    if assets_change:
        # if assets_change and not "eugen" in root_folder:
        process_delete_web_view = subprocess.Popen("aws s3 rm s3://" + lambda_constants["cdn_bucket"] + "/assets/web_view --recursive", shell=True)
        process_delete_fonts = subprocess.Popen("aws s3 rm s3://" + lambda_constants["cdn_bucket"] + "/assets/fonts --recursive", shell=True)
        process_delete_icons = subprocess.Popen("aws s3 rm s3://" + lambda_constants["cdn_bucket"] + "/assets/icons --recursive", shell=True)
        process_delete_images = subprocess.Popen("aws s3 rm s3://" + lambda_constants["cdn_bucket"] + "/assets/images --recursive", shell=True)
        process_delete_videos = subprocess.Popen("aws s3 rm s3://" + lambda_constants["cdn_bucket"] + "/assets/videos --recursive", shell=True)

        process_delete_web_view.wait()
        process_delete_fonts.wait()
        process_delete_icons.wait()
        process_delete_images.wait()
        process_delete_videos.wait()

        process_copy_web_view = subprocess.Popen("aws s3 cp " + str(root_folder) + "src/assets/web_view s3://" + lambda_constants["cdn_bucket"] + "/assets/web_view --recursive", shell=True)
        process_copy_fonts = subprocess.Popen("aws s3 cp " + str(root_folder) + "src/assets/fonts s3://" + lambda_constants["cdn_bucket"] + "/assets/fonts --recursive", shell=True)
        process_copy_icons = subprocess.Popen("aws s3 cp " + str(root_folder) + "src/assets/icons s3://" + lambda_constants["cdn_bucket"] + "/assets/icons --recursive", shell=True)
        process_copy_images = subprocess.Popen("aws s3 cp " + str(root_folder) + "src/assets/images s3://" + lambda_constants["cdn_bucket"] + "/assets/images --recursive", shell=True)
        process_copy_videos = subprocess.Popen("aws s3 cp " + str(root_folder) + "src/assets/videos s3://" + lambda_constants["cdn_bucket"] + "/assets/videos --recursive", shell=True)

        process_copy_web_view.wait()
        process_copy_fonts.wait()
        process_copy_icons.wait()
        process_copy_images.wait()
        process_copy_videos.wait()

        cloudfront_client = client("cloudfront")
        list_distributions_response = cloudfront_client.list_distributions()
        for distribution in list_distributions_response["DistributionList"]["Items"]:
            if "AliasICPRecordals" in distribution:
                if "cdn.augin.app" in distribution["AliasICPRecordals"][0]["CNAME"]:
                    print("Invalidating " + distribution["AliasICPRecordals"][0]["CNAME"])
                    create_invalidation(cloudfront_client, distribution["Id"])

    update_lambda_thread.join()

    print("UPDATE COMPLETED | TIME TAKEN " + str(time() - start_time))

    delete_folder_contents(s3_client, lambda_constants["cdn_bucket"], "style/", new_version)
    delete_folder_contents(s3_client, lambda_constants["cdn_bucket"], "js/", new_version)

    with open("src/html/main/header.html", "r") as read_file:
        header = read_file.read()
    header = header.replace("style_" + new_version + ".css", "style.css")
    header = header.replace("index_" + new_version + ".js", "index.js")
    ###
    with open("src/html/main/header.html", "w") as read_file:
        read_file.write(header)

    with open("last_update_data.json", "w") as outfile:
        json.dump(last_update_data, outfile)


start_time = time()
run()
print("final")
