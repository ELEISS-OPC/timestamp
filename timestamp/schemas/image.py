from pydantic import BaseModel, Field


class S3Config(BaseModel):
    """
    Configuration settings for S3 storage.

    Attributes
    ----------
    endpoint_url : str
        The endpoint URL of the S3 service.
    access_key : str
        The access key for S3 authentication.
    secret_key : str
        The secret key for S3 authentication.
    bucket_name : str
        The name of the S3 bucket to use. Default is "timestamp-selfies".
    region : str
        The region where the S3 bucket is located. Default is "apac" (Asia Pacific).
    """

    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str = "timestamp-selfies"
    region: str = "apac"


class ImageSet(BaseModel):
    """
    Represents a set of images including the original and its preview.
    """

    original: str = Field(
        ..., description="Original image", examples=["123940712123.jpg"]
    )
    preview: str = Field(
        ..., description="Preview image", examples=["1412312341234.jpg"]
    )

class ImageUploadRequest(BaseModel):
    """
    Request model for uploading an image in base64 format.

    Attributes
    ----------
    image : str
        The base64-encoded image string.
    """

    image: str = Field(
        ...,
        description="Base64-encoded image string.",
        examples=[
            "iVBORw0KGgoAAAANSUhEUgAAAAUA"
            "AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHx"
            "gljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
        ],
    )