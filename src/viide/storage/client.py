from datetime import timedelta
from typing import TYPE_CHECKING, BinaryIO

import boto3
from botocore.config import Config
from pydantic import AnyUrl, HttpUrl, SecretStr

from viide.app.storage import Storage

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


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
        self.client.upload_fileobj(
            stream, self.bucket, key, ExtraArgs={"ContentType": content_type}
        )

    def get(self, key: str, expires_in: timedelta) -> HttpUrl:
        return HttpUrl(
            self.signer.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=int(expires_in.total_seconds()),
            )
        )

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

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
