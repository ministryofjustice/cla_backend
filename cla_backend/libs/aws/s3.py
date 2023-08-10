from tempfile import NamedTemporaryFile
from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError


class ClientError(ClientError):
    pass


class StaticS3Storage(S3Boto3Storage):
    default_acl = "public-read"


class ReportsS3:
    @classmethod
    def clean_name(cls, name):
        return name.strip("/")

    @classmethod
    def get_s3_connection(cls, bucket_name):
        return S3Boto3Storage(bucket=bucket_name)

    @classmethod
    def download_file(cls, bucket_name, key):
        try:
            obj = cls.get_s3_connection(bucket_name).bucket.Object(cls.clean_name(key))
            data = NamedTemporaryFile()
            obj.download_fileobj(data)
            data.seek(0)
            return {"headers": {"Content-Type": obj.content_type}, "body": data}
        except ClientError:
            return None

    @classmethod
    def save_file(cls, bucket_name, key, path):
        cls.get_s3_connection(bucket_name).bucket.Object(cls.clean_name(key)).upload_file(path)

    @classmethod
    def delete_file(cls, bucket_name, key):
        cls.get_s3_connection(bucket_name).delete(cls.clean_name(key))

    @classmethod
    def save_data_to_bucket(cls, bucket_name, key, content):
        cls.get_s3_connection(bucket_name).bucket.Object(key).put(Body=content)
