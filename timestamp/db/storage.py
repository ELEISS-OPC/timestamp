import boto3
from botocore import client

from timestamp.core.config import env
from timestamp.schemas.image import S3Config

s3_config = S3Config(
    endpoint_url=env.S3_ENDPOINT_URL,
    access_key=env.S3_ACCESS_KEY,
    secret_key=env.S3_SECRET_KEY,
    bucket_name=env.S3_BUCKET_NAME,
    region=env.S3_REGION,
)

s3_storage: client.BaseClient = boto3.client(
    "s3",
    endpoint_url=s3_config.endpoint_url,
    aws_access_key_id=s3_config.access_key,
    aws_secret_access_key=s3_config.secret_key,
    region_name=s3_config.region,
)

# Make this information available everywhere
# Since there will be only one bucket used in this application
setattr(s3_storage, "bucket_name", s3_config.bucket_name)
