import os
import json
from utils.Config import lambda_constants
from utils.AWS.S3 import S3
from utils.AWS.Ses import Ses
from utils.AWS.Dynamo import Dynamo
from utils.utils.ReadWrite import ReadWrite
from fbx import FbxManager
from fbx import FbxScene
from fbx import FbxImporter
from fbx import FbxExporter


FBX_BINARY_SIGNATURE = b"Kaydara FBX Binary  \x00\x1A\x00"
FBX_BINARY_SIGNATURE_LENGTH = len(FBX_BINARY_SIGNATURE)
FBX_MANAGER = FbxManager.Create()

ZIP_FILE_PATH = lambda_constants["tmp_path"] + "model.zip"
FBX_FOLDER_PATH = lambda_constants["tmp_path"] + "model"


def _get_file_fomrat(format_name):
    io_plugin_registry = FBX_MANAGER.GetIOPluginRegistry()
    for format_id in range(io_plugin_registry.GetWriterFormatCount()):
        if io_plugin_registry.WriterIsFBX(format_id):
            desc = io_plugin_registry.GetWriterFormatDescription(format_id)
            if format_name in desc:
                return format_id
    # Default format is auto
    return -1


def convert_ascii_to_binary(path):
    if _is_binary_fbx(path) == False:
        print(f"Convert {path} ASCII to Binary")
        scene = FbxScene.Create(FBX_MANAGER, "")
        importer = FbxImporter.Create(FBX_MANAGER, "")
        importer.Initialize(path, -1)
        importer.Import(scene)
        importer.Destroy()
        exporter = FbxExporter.Create(FBX_MANAGER, "")
        exporter.Initialize(path, _get_file_fomrat("binary"))
        exporter.Export(scene)
        exporter.Destroy()
        scene.Destroy()
        print("Finished conversion")
    else:
        print("This fbx has a binary format already")


def _is_binary_fbx(path):
    with open(path, "rb") as file:
        return file.read(FBX_BINARY_SIGNATURE_LENGTH) == FBX_BINARY_SIGNATURE
    return False


def lambda_handler(event, context):
    try:
        return main_lambda_handler(event, context)
    except Exception as e:
        Ses().send_error_email(event, "lambda_process_fbx_to_glb", e)


def main_lambda_handler(event, context):
    ReadWrite().delete_files_inside_a_folder(lambda_constants["tmp_path"])

    model = Dynamo().get_model_by_id(event["model_id"])
    S3().download_file(lambda_constants["processed_bucket"], model["model_upload_path_zip"], ZIP_FILE_PATH)
    ReadWrite().extract_zip_file(ZIP_FILE_PATH, FBX_FOLDER_PATH)
    fbx_location = ReadWrite().find_file_with_extension_in_directory(FBX_FOLDER_PATH, ["fbx"])
    convert_ascii_to_binary(fbx_location)
    # convert_fbx_to_glb(fbx_location)

    print(json.dumps(event))
    return


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow_lambda_process_fbx_to_glb.json", "r") as read_file:
        event = json.load(read_file)
        html = main_lambda_handler(event, None)
    print("END")
