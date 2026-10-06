import boto3
from mypy_boto3_s3 import S3Client

from viide.config import Settings


def create_client(settings: Settings) -> S3Client:
    return boto3.client(
        "s3",
        endpoint_url=str(settings.storage_endpoint),
        aws_access_key_id=settings.storage_access_key.get_secret_value(),
        aws_secret_access_key=settings.storage_secret_key.get_secret_value(),
    )
