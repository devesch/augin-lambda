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
import bpy
import time

FBX_BINARY_SIGNATURE = b"Kaydara FBX Binary  \x00\x1A\x00"
FBX_BINARY_SIGNATURE_LENGTH = len(FBX_BINARY_SIGNATURE)
FBX_MANAGER = FbxManager.Create()

def _time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  print("Time Lapsed = {0:02}:{1:02}:{2:02}".format(int(hours),int(mins),sec))

def _get_file_fomrat(format_name):
    io_plugin_registry = FBX_MANAGER.GetIOPluginRegistry()
    for format_id in range(io_plugin_registry.GetWriterFormatCount()):
        if io_plugin_registry.WriterIsFBX(format_id):
            desc = io_plugin_registry.GetWriterFormatDescription(format_id)
            if format_name in desc:
                return format_id
    # Default format is auto
    return -1

def _is_binary_fbx(path):
    with open(path, 'rb') as file:
        return file.read(FBX_BINARY_SIGNATURE_LENGTH) == FBX_BINARY_SIGNATURE
    return False

def convert_ascii_to_binary(path):
    if _is_binary_fbx(path) == False:
        print(f"Convert {path} ASCII to Binary")
        scene = FbxScene.Create(FBX_MANAGER, "")
        importer = FbxImporter.Create(FBX_MANAGER, "")
        importer.Initialize(path, -1)
        importer.Import(scene)
        importer.Destroy()
        exporter = FbxExporter.Create(FBX_MANAGER, "")
        exporter.Initialize(path, _get_file_fomrat('binary'))
        exporter.Export(scene)
        exporter.Destroy()
        scene.Destroy()
        print("Finished conversion ASCII to Binary")
    else:
        print("This FBX has a Binary format already")

def convert_fbx_to_glb(path):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    print("Start Import FBX scene")
    bpy.ops.import_scene.fbx(filepath=path)
    bpy.ops.object.scale_clear()
    print("End Import FBX scene")
    output_path = path.replace(".fbx", "")
    print("Start conversion FBX to GLB")
    bpy.ops.export_scene.gltf(filepath=output_path)
    print("Finished conversion FBX to GLB")

def convert(path):
    start_time = time.time()
    convert_ascii_to_binary(path)
    convert_fbx_to_glb(path)
    end_time = time.time()
    time_lapsed = end_time - start_time
    _time_convert(time_lapsed)

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
    convert(fbx_location)

    print(json.dumps(event))
    return


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow_lambda_process_fbx_to_glb.json", "r") as read_file:
        event = json.load(read_file)
        html = main_lambda_handler(event, None)
    print("END")
