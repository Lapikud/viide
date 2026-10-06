from datetime import timedelta
from typing import TYPE_CHECKING, BinaryIO

import boto3
from boto3.exceptions import S3UploadFailedError
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import AnyUrl, HttpUrl, SecretStr

from viide.app.storage import Storage, StorageUnavailable

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client

STORAGE_ERRORS = (BotoCoreError, ClientError, S3UploadFailedError)


class S3Storage(Storage):
    def __init__(
        self,
        endpoint: AnyUrl,
        public_endpoint: AnyUrl,
        access_key: SecretStr,
        secret_key: SecretStr,
        bucket: str,
    ) -> None:
        self.client = self.__create_client(endpoint, access_key, secret_key)
        self.signer = self.__create_client(public_endpoint, access_key, secret_key)
        self.bucket = bucket

    def put(self, key: str, stream: BinaryIO, content_type: str) -> None:
        try:
            self.client.upload_fileobj(
                stream, self.bucket, key, ExtraArgs={"ContentType": content_type}
            )
        except STORAGE_ERRORS as e:
            raise StorageUnavailable from e

    def get(self, key: str, expires_in: timedelta) -> HttpUrl:
        try:
            url = self.signer.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=int(expires_in.total_seconds()),
            )
        except STORAGE_ERRORS as e:
            raise StorageUnavailable from e
        return HttpUrl(url)

    def delete(self, key: str) -> None:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except STORAGE_ERRORS as e:
            raise StorageUnavailable from e

    def __create_client(
        self, endpoint: AnyUrl, access_key: SecretStr, secret_key: SecretStr
    ) -> "S3Client":
        return boto3.client(
            "s3",
            endpoint_url=str(endpoint),
            aws_access_key_id=access_key.get_secret_value(),
            aws_secret_access_key=secret_key.get_secret_value(),
            config=Config(signature_version="s3v4"),
        )
