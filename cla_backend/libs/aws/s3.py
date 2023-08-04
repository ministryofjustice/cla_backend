from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError


class StaticS3Storage(S3Boto3Storage):
    default_acl = "public-read"


class ReportsS3:
    @classmethod
    def get_s3_connection(cls, bucket_name):
        return StaticS3Storage(bucket=bucket_name)

    @classmethod
    def download_file(cls, bucket_name, key):
        try:
            response = cls.get_s3_connection(bucket_name).bucket.Object(key).get()
        except ClientError:
            return None

        return {"headers": {"Content-Type": response["ContentType"]}, "body": response["Body"]}

    @classmethod
    def save_file(cls, bucket_name, key, path):
        cls.get_s3_connection(bucket_name).save(key, open(path, "rb"))

    @classmethod
    def delete_file(cls, bucket_name, key):
        cls.get_s3_connection(bucket_name).delete(key)

    @classmethod
    def save_data_to_bucket(cls, bucket_name, key, content):
        cls.get_s3_connection(bucket_name).bucket.Object(key).put(Body=content)
