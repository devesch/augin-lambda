import json
import os
from utils.Code import Code

codes = {}


class ReadWrite:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ReadWrite, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def write_bytes(self, bytes_content, output_file_path):
        with open(output_file_path, "wb") as pdf_file:
            pdf_file.write(bytes_content)

    def read_file_with_codecs(self, file_path):
        import codecs

        with codecs.open(file_path, "r", "utf-8-sig") as read_file:
            return read_file.read()

    def write_file_with_codecs(self, file_path, file_data):
        import codecs

        with codecs.open(file_path, "w", "utf-8-sig") as write_file:
            write_file.write(file_data)

    def find_file_with_extension_in_directory(self, root_directory, extensions):
        import os

        for root, dirs, files in os.walk(root_directory):
            for file in files:
                for extension in extensions:
                    if file.lower().endswith("." + extension.lower()):
                        return os.path.join(root, file).replace("\\", "/")

        return None

    def get_file_hash(self, file_path):
        import hashlib

        hash_function = hashlib.sha256()
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_function.update(chunk)
        return hash_function.hexdigest()

    def zip_file(self, file_to_be_ziped_location, zip_destiny_location):
        import zipfile

        with zipfile.ZipFile(zip_destiny_location, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as myzip:
            myzip.write(file_to_be_ziped_location, arcname=os.path.basename(file_to_be_ziped_location))

    def zip_folder(self, folder_to_be_ziped_location, zip_destiny_location):
        import zipfile
        import os

        with zipfile.ZipFile(zip_destiny_location, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_to_be_ziped_location):
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, folder_to_be_ziped_location)
                    zipf.write(full_path, relative_path)

    def read_html(self, filename, common_changes=None):
        import copy

        global codes
        code = codes.get(filename)
        if code and os.environ.get("AWS_EXECUTION_ENV"):
            new_code = copy.deepcopy(code)
            new_code.common_changes = common_changes
        else:
            codes[filename] = Code(filename)
            new_code = copy.deepcopy(codes[filename])
            new_code.common_changes = common_changes
        # if lambda_constants["debug"]:
        #     new_code.esc("show_only_when_debug_val", "")
        # else:
        #     new_code.esc("show_only_when_debug_val", "display:none;")
        return new_code

    def extract_zip_file(self, zip_file_path, extract_path):
        import zipfile

        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

    def read_xml_file(self, file_path):
        import xml.etree.ElementTree as ET

        data = self.read_file_with_codecs(file_path)
        tree = ET.ElementTree(ET.fromstring(data))
        return tree

    def read_file(self, file_path):
        with open(file_path, "r") as read_file:
            return read_file.read()

    def read_json(self, file_path):
        return json.load(open(file_path, "r", encoding="utf-8"))

    def read_file_with_codecs(self, file_path):
        import codecs

        with codecs.open(file_path, "r", "utf-8-sig") as read_file:
            return read_file.read()

    def read_bytes(self, file_path):
        with open(file_path, "rb") as read_file:
            return read_file.read()

    def read_excel(self, file_path, sheet_name):
        import pandas

        df = pandas.read_excel(io=file_path, sheet_name=sheet_name, header=0, keep_default_na=False)
        return df.to_dict("records")

    def read_csv(self, file_path):
        import csv

        records = []
        with open(file_path, "r", encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                records.append(dict(row))
        return records

    def write_file(self, file_path, file_data):
        with open(file_path, "w") as write_file:
            write_file.write(file_data)

    def write_json_file(self, file_path, file_data):
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(file_data, json_file, sort_keys=True, ensure_ascii=False, indent=4)

    def delete_files_inside_a_folder(self, path_to_folder):
        import os, shutil

        for filename in os.listdir(path_to_folder):
            file_path = os.path.join(path_to_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
