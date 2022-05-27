from typing import Optional
import boto3
from botocore.client import BaseClient

from config.S3_config import *


# Handler for AWS S3 Storage
class S3Handler:
    def __init__(self, bucket_name: str):
        self.__client: Optional[BaseClient] = None
        self.__bucket_name: str = bucket_name

    def connect(self):
        """
        Connect to the storage (AWS S3 storage)
        :return: None
        """
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
        """
        Upload the file to S3 storage.
        :param local_path: local path
        :param remote_path: remote path in S3 storage
        :return: Whether uploading job is successful
        """
        try:
            self.__client.upload_file(local_path, self.__bucket_name, remote_path)
        except Exception as e:
            print(e)
            return False
        return True

    # Download file from s3 bucket
    def download(self, remote_path: str, local_path: str) -> bool:
        """
        Download the file from storage.
        :param remote_path: remote path in S3 storage
        :param local_path: local path
        :return: Whether Downloading job is successful
        """
        try:
            self.__client.download_file(self.__bucket_name, remote_path, local_path)
        except Exception as e:
            print(e)
            return False
        return True

    """
    generate_presigned_url(ClientMethod, Params=None, ExpiresIn=3600, HttpMethod=None)
Generate a presigned url given a client, its method, and arguments

Parameters
ClientMethod (string) -- The client method to presign for
Params (dict) -- The parameters normally passed to ClientMethod.
ExpiresIn (int) -- The number of seconds the presigned url is valid for. By default it expires in an hour (3600 seconds)
HttpMethod (string) -- The http method to use on the generated url. By default, the http method is whatever is used in the method's model.
Returns
The presigned url
    """

    def generate_presigned_url(self):
        expire_time: int = 60
        http_method: str = "post"
        # upload a file to a bucket with generate_presigned_url with put object
        # self.__client.download_file(self.__bucket_name, remote_path, local_path)
        url = self.__client.generate_presigned_url('get_object', Params={'Bucket': self.__bucket_name,
                                                                         "Key": "glb/wordnumperiod202205-2617-4910-bdb9717a-e879-4e52-b4e7-8ac140dbbde9.glb"},
                                                   ExpiresIn=expire_time)
        print(url)


handler = S3Handler(AWS_S3_BUCKET_NAME)
handler.connect()
handler.generate_presigned_url()
