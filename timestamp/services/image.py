import base64
from functools import cached_property
from hashlib import md5
from io import BytesIO

from botocore import client
from PIL import Image, ImageFile

from timestamp.schemas.enums import ImageFormat
from timestamp.schemas.image import ImageSet
from timestamp.utils.errors import DecodingError, UnsupportedImageFormatError


class ImageService:
    def __init__(
        self,
        s3: client.BaseClient,
    ):
        """
        Initialize the ImageService with S3 client.

        Parameters
        ----------
        s3 : client.BaseClient
            The S3 client for interacting with the S3 storage.
        """
        self.s3 = s3

    def upload_image(self, image: bytes) -> ImageSet:
        """
        Upload an image to the S3 bucket.

        Parameters
        ----------
        image_bytes : bytes
            The image data in bytes.

        Returns
        -------
        ImageSet
            The set of uploaded images including original and preview.
        """
        buffer = BytesIO(image)
        buffer.seek(0)

        format = self._determine_format(buffer)
        self._validate_format(format)
        original_image_name = self._build_image_name(image, format)

        preview_image = self._generate_image_preview(image)
        preview_buffer = BytesIO(preview_image)
        preview_buffer.seek(0)

        preview_image_name = self._build_image_name(preview_image, format)

        self._upload_to_s3(original_image_name, buffer, format)
        self._upload_to_s3(preview_image_name, preview_buffer, format)

        return ImageSet(original=original_image_name, preview=preview_image_name)

    def upload_image_base64(self, image: str) -> ImageSet:
        """
        Upload a base64-encoded image to the S3 bucket.

        Parameters
        ----------
        image : str
            The base64-encoded image string.

        Returns
        -------
        ImageSet
            The set of uploaded images including original and preview.
        """
        try:
            # Decode base64 to bytes
            image_bytes = base64.b64decode(image)
        except Exception:
            raise DecodingError()

        return self.upload_image(image_bytes)

    def _upload_to_s3(self, filename: str, data: BytesIO, format: str) -> None:
        """
        Upload a file-like object to the S3 bucket.

        Parameters
        ----------
        filename : str
            The name of the file in the S3 bucket.
        data : BytesIO
            The file data as a file-like object.
        format : str
            The content type of the file (e.g., "jpeg").
        """
        self.s3.upload_fileobj(
            Bucket=self.s3.bucket_name,
            Key=filename,
            Fileobj=data,
            ExtraArgs={"ContentType": f"image/{format.lower()}"},
        )

    @staticmethod
    def _build_image_name(image_bytes: bytes, format: str) -> str:
        """
        Build a unique image name based on the MD5 hash of the image bytes.
        Parameters
        ----------
        image_bytes : bytes
            The image data in bytes.
        format : str
            The image format.

        Returns
        -------
        str
            The generated image name.
        """
        image_hash = md5(image_bytes).hexdigest()
        return f"{image_hash}.{format}"

    @staticmethod
    def _determine_format(image: BytesIO) -> str:
        """
        Determine the format of the given image bytes.


        Parameters
        ----------
        image : BytesIO
            The image data in bytes.

        Returns
        -------
        str
            The format of the image.
        """
        ## Open regardless of truncated images
        ImageFile.LOAD_TRUNCATED_IMAGES = True  # type: ignore
        image.seek(0)
        with Image.open(image) as img:
            image.seek(0)

            if img.format is None:
                raise UnsupportedImageFormatError(format="unknown")

            return img.format.lower()

    def _validate_format(self, format: str) -> None:
        """
        Validate if the given image format is supported.

        Parameters
        ----------
        format : str
            The image format to validate.

        Raises
        ------
        UnsupportedImageFormatError
            If the image format is not supported.
        """
        if format.lower() not in self._supported_formats:
            raise UnsupportedImageFormatError(format=format.lower())

    @cached_property
    def _supported_formats(self) -> set[str]:
        """
        Return the set of supported image formats.
        """
        return {fmt.value.lower() for fmt in ImageFormat}

    def _generate_image_preview(
        self, image: bytes, size: tuple[int, int] = (256, 256)
    ) -> bytes:
        """
        Generate a preview of the image with the specified size.

        Parameters
        ----------
        image_name : str
            The name of the image in the S3 bucket.
        size : tuple[int, int]
            The desired size (width, height) of the preview. Default is (256, 256).

        Returns
        -------
        bytes
            The preview image data in bytes.
        """
        buffer = BytesIO(image)
        buffer.seek(0)

        with Image.open(buffer) as img:
            img.thumbnail(size)
            preview_buffer = BytesIO()
            img.save(preview_buffer, format=img.format)
            preview_buffer.seek(0)
            return preview_buffer.read()
