from json import dumps, load
import traceback
from PIL import Image
import os
import pillow_avif
import boto3
from utils.AWS.S3 import S3
from utils.AWS.Ses import Ses


if not "AWS_EXECUTION_ENV" in os.environ:
    save_path = "tmp/my_local_image"
else:
    save_path = "/tmp/my_local_image"


def main_lambda_handler(event, context):
    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]
        try:
            key_format = key.split(".")[1]
            key_without_format = key.split(".")[0]
        except:
            key_format = ""
            key_without_format = key
        if key_format == "new" or key_format == "jpg" or key_format == "jpeg" or key_format == "png" or key_format == "":
            convert_image_to_all_formats(bucket, key, key_format, key_without_format)
            print("valid image format")
        print("end")
        return
    except:
        print("No record action")
        return


def lambda_handler(event, context):
    print(dumps(event))
    try:
        return main_lambda_handler(event, context)
    except Exception as e:
        Ses().send_error_email(event, "lambda_format_images", e)


def convert_image_to_all_formats(bucket, key, key_format, key_without_format):
    if not S3().download_file(bucket, key, key_format):
        return

    img_PIL = Image.open((save_path + key_format), "r", None)

    if key_format.lower() == "png":
        if not check_if_image_exists(bucket, key_without_format + ".avif"):
            img_PIL.save(save_path + "avif", "AVIF")
            upload_image_to_s3(bucket, key_without_format, "avif")
        if not check_if_image_exists(bucket, key_without_format + ".webp"):
            img_PIL.save(save_path + "webp", "WEBP")
            upload_image_to_s3(bucket, key_without_format, "webp")
        if not check_if_image_exists(bucket, key_without_format + ".jpeg"):
            img_PIL = img_PIL.convert("RGB")
            img_PIL.save(save_path + "jpeg", "JPEG")
            upload_image_to_s3(bucket, key_without_format, "jpeg")

    elif key_format.lower() == "new":
        if not check_if_image_exists(bucket, key_without_format + ".jpeg"):
            img_PIL = img_PIL.convert("RGB")
            img_PIL.save(save_path + "jpeg", "JPEG")
            upload_image_to_s3(bucket, key_without_format, "jpeg")
        img_PIL = img_PIL.convert("RGBA")
        if not check_if_image_exists(bucket, key_without_format + ".avif"):
            img_PIL.save(save_path + "avif", "AVIF")
            upload_image_to_s3(bucket, key_without_format, "avif")
        if not check_if_image_exists(bucket, key_without_format + ".webp"):
            img_PIL.save(save_path + "webp", "WEBP")
            upload_image_to_s3(bucket, key_without_format, "webp")
        if not check_if_image_exists(bucket, key_without_format + ".png"):
            img_PIL.save(save_path + "png", "PNG")
            upload_image_to_s3(bucket, key_without_format, "png")

    elif key_format.lower() == "":
        if not check_if_image_exists(bucket, key_without_format + ".jpeg"):
            img_PIL = img_PIL.convert("RGB")
            img_PIL.save(save_path + "jpeg", "JPEG")
            upload_image_to_s3(bucket, key_without_format, "jpeg")
        img_PIL = img_PIL.convert("RGBA")
        if not check_if_image_exists(bucket, key_without_format + ".avif"):
            img_PIL.save(save_path + "avif", "AVIF")
            upload_image_to_s3(bucket, key_without_format, "avif")
        if not check_if_image_exists(bucket, key_without_format + ".webp"):
            img_PIL.save(save_path + "webp", "WEBP")
            upload_image_to_s3(bucket, key_without_format, "webp")
        if not check_if_image_exists(bucket, key_without_format + ".png"):
            img_PIL.save(save_path + "png", "PNG")
            upload_image_to_s3(bucket, key_without_format, "png")

    elif key_format.lower() == "jpg" or key_format.lower() == "jpeg":
        if not check_if_image_exists(bucket, key_without_format + ".jpeg"):
            img_PIL = img_PIL.convert("RGB")
            img_PIL.save(save_path + "jpeg", "JPEG")
            upload_image_to_s3(bucket, key_without_format, "jpeg")
        img_PIL = img_PIL.convert("RGBA")
        if not check_if_image_exists(bucket, key_without_format + ".avif"):
            img_PIL.save(save_path + "avif", "AVIF")
            upload_image_to_s3(bucket, key_without_format, "avif")
        if not check_if_image_exists(bucket, key_without_format + ".webp"):
            img_PIL.save(save_path + "webp", "WEBP")
            upload_image_to_s3(bucket, key_without_format, "webp")
        if not check_if_image_exists(bucket, key_without_format + ".png"):
            img_PIL.save(save_path + "png", "PNG")
            upload_image_to_s3(bucket, key_without_format, "png")
    else:
        print("Error! Image: " + save_path + "." + key_format + " could not be converted.")

    img_PIL = ""


def check_if_image_exists(bucket, key):
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except:
        print("Image doesnt exist")
        return False


if os.environ.get("AWS_EXECUTION_ENV") is None:
    with open("_testnow.json", "r") as read_file:
        event = load(read_file)
        # start = time()
        html = main_lambda_handler(event, None)
        # print("Tempo: " + str(time() - start))
    print("END")
