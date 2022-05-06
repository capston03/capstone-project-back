# import module
import boto3

from s3_config import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY
from s3_config import AWS_S3_BUCKET_NAME, AWS_S3_BUCKET_REGION


def s3_connection():
    """
    Connect to s3 bucket.

    :return: s3 connection object
    """
    try:
        s3 = boto3.client(
            service_name='s3',
            region_name=AWS_S3_BUCKET_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    except Exception as e:
        print(e)
        exit(-1)
    else:
        print("s3 bucket connected!")
        return s3


def s3_put_object(s3, bucket, filepath, object_name) -> bool:
    """
    Upload file to s3 bucket.

    :param s3: s3 connection object (boto3 client)
    :param bucket: bucket name
    :param filepath: file directory
    :param object_name: Name of object that will be saved in s3 object
    :return: sucess-> True, failure-> False
    """
    try:
        s3.upload_file(filepath, bucket, object_name)
    except Exception as e:
        print(e)
        return False
    return True


def s3_get_object(s3, bucket, object_name, file_name):
    """
    Download file from s3 bucket.

    :param s3: s3 connection object (boto3 client)
    :param bucket: bucket name
    :param object_name: Name of object saved in s3 bucket
    :param file_name: file name
    :return: sucess-> True, failure-> False
    """
    try:
        s3.download_file(bucket, object_name, file_name)
    except Exception as e:
        print(e)
        return False
    return True
