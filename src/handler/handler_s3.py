# import module
from typing import Optional
import boto3
from botocore.client import BaseClient

from config.S3_config import *


class S3Handler:
    def __init__(self, bucket_name: str):
        self.__client: Optional[BaseClient] = None
        self.__bucket_name: str = bucket_name

    # Connect to s3 bucket
    def connect(self):
        try:
            self.__client = boto3.client(
                service_name='s3',
                region_name=AWS_S3_BUCKET_REGION,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            print(e)
            exit(-1)

    # Upload file to s3 bucket
    def upload(self, local_path: str, remote_path: str) -> bool:
        try:
            self.__client.upload_file(local_path, self.__bucket_name, remote_path)
        except Exception as e:
            print(e)
            return False
        return True

    # Download file from s3 bucket
    def download(self, remote_path: str, local_path: str) -> bool:
        try:
            self.__client.download_file(self.__bucket_name, remote_path, local_path)
        except Exception as e:
            print(e)
            return False
        return True


handler = S3Handler(AWS_S3_BUCKET_NAME)
handler.connect()