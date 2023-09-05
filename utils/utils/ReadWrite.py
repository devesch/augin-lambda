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

    def find_file_with_extension_in_directory(self, root_directory, extensions):
        import os

        for root, dirs, files in os.walk(root_directory):
            for file in files:
                for extension in extensions:
                    if file.lower().endswith("." + extension.lower()):
                        return os.path.join(root, file).replace("\\", "/")

        return None

    def zip_file(self, file_to_be_ziped_location, zip_destiny_location):
        import zipfile

        with zipfile.ZipFile(zip_destiny_location, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as myzip:
            myzip.write(file_to_be_ziped_location, arcname=os.path.basename(file_to_be_ziped_location))
            print("Zip Generated " + zip_destiny_location)

    def read_html(self, filename, common_changes=None):
        import copy

        global codes

        code = codes.get(filename)
        if code:
            new_code = copy.deepcopy(code)
            new_code.common_changes = common_changes
            return new_code
        codes[filename] = Code(filename)
        new_code = copy.deepcopy(codes[filename])
        new_code.common_changes = common_changes
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
