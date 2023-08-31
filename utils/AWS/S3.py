from utils.Config import lambda_constants

s3_resource = None
s3_client = None
us_s3_client = None
temp_s3_client = None


class S3:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(S3, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def get_bucket_from_bucket_url(self, bucket_url):
        if lambda_constants["cdn"] in bucket_url:
            return lambda_constants["cdn_bucket"]
        elif lambda_constants["img_cdn"] in bucket_url:
            return lambda_constants["img_bucket"]
        elif "upload.pauluzzi.com.br" in bucket_url:
            return "upload.pauluzzi.com.br"
        elif ".s3.sa-east-1.amazonaws.com/" in bucket_url:
            parts = bucket_url.split(".s3.sa-east-1.amazonaws.com/")
            if "https://" in parts[0]:
                return parts[0].split("https://")[1]
        else:
            parts = bucket_url.split("/")
            return parts[2]

    def get_key_from_bucket_url(self, bucket_url):
        if lambda_constants["cdn"] in bucket_url:
            return bucket_url.replace(lambda_constants["cdn"], "")[1:]
        elif lambda_constants["img_cdn"] in bucket_url:
            return bucket_url.replace(lambda_constants["img_cdn"], "")[1:]
        elif "upload.pauluzzi.com.br" in bucket_url:
            return bucket_url.split("upload.pauluzzi.com.br/")[1]
        elif ".s3.sa-east-1.amazonaws.com/" in bucket_url:
            parts = bucket_url.split(".s3.sa-east-1.amazonaws.com/")
            return parts[1]
        else:
            parts = bucket_url.split("/")
            return "/".join(parts[4:])

    def generate_presigned_url(self, bucket, key, expire_time=3600):
        return self.get_temp_s3_client().generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expire_time)

    def generate_presigned_post(self, bucket, key, file_mimetype=None, expire_time=3600):
        if not file_mimetype:
            return self.get_temp_s3_client().generate_presigned_post(Bucket=bucket, Key=key, ExpiresIn=int(expire_time))
        fields = {"Content-Type": file_mimetype}
        conditions = [{"Content-Type": file_mimetype}]
        return self.get_temp_s3_client().generate_presigned_post(Bucket=bucket, Key=key, Fields=fields, Conditions=conditions, ExpiresIn=int(expire_time))

    def download_file_from_link(self, s3_url, file_path):
        s3_url_parts = s3_url.split("/")
        bucket_name = s3_url_parts[2]
        object_key = "/".join(s3_url_parts[3:])
        self.get_s3_client().download_file(bucket_name, object_key, file_path)

    def download_file(self, bucket, key, file_path, region=lambda_constants["region"]):
        if region == "us_east_1":
            self.get_us_s3_client().download_file(bucket, key, file_path)
        else:
            self.get_s3_client().download_file(bucket, key, file_path)

    def delete_folder(self, bucket, key_prefix):
        bucket = self.get_s3_resource().Bucket(bucket)
        bucket.objects.filter(Prefix=key_prefix + "/").delete()
        return True

    def check_if_file_exists(self, bucket, key):
        try:
            self.get_s3_client().head_object(Bucket=bucket, Key=key)
            return True
        except:
            return False

    def get_filesize(self, bucket, key):
        try:
            head_response = self.get_s3_client().head_object(Bucket=bucket, Key=key)
            return head_response["ContentLength"]
        except:
            return "0"

    def get_filesize(self, bucket, key):
        response = self.get_s3_client().head_object(Bucket=bucket, Key=key)
        return str(response["ContentLength"])

    def upload_file(self, bucket, key, file_path):
        self.get_s3_client().upload_file(file_path, bucket, key)
        return True

    def list_files_from_folder(self, bucket, prefix=""):
        response = self.get_s3_client().list_objects(Bucket=bucket, Prefix=prefix)
        return response.get("Contents", [])

    def delete_file(self, bucket, key):
        self.get_s3_client().delete_object(Bucket=bucket, Key=key)

    def copy_file_from_one_bucket_to_another(self, source_bucket, source_key, destination_bucket, destination_key):
        import time

        self.get_s3_client().copy_object(Bucket=destination_bucket, CopySource={"Bucket": source_bucket, "Key": source_key}, Key=destination_key)
        time.sleep(3)

    def get_s3_client(self):
        global s3_client
        if s3_client:
            return s3_client
        import boto3

        s3_client = boto3.client("s3", lambda_constants["region"])
        return s3_client

    def get_s3_resource(self):
        global s3_resource
        if s3_resource:
            return s3_resource
        import boto3
        from botocore.config import Config

        config = Config(retries={"max_attempts": 50}, max_pool_connections=50)
        s3_resource = boto3.resource("s3", config=config, region_name=lambda_constants["region"])
        return s3_resource

    def get_temp_s3_client(self):
        global temp_s3_client
        if temp_s3_client:
            return temp_s3_client
        import boto3

        temp_s3_client = boto3.client("s3", lambda_constants["region"], aws_access_key_id=lambda_constants["s3_put_user_key_id"], aws_secret_access_key=lambda_constants["s3_put_user_secret_access_key"])
        return temp_s3_client

    def get_us_s3_client(self):
        global us_s3_client
        if us_s3_client:
            return us_s3_client
        import boto3

        us_s3_client = boto3.client("s3", region_name="us-east-1")
        return us_s3_client
