class UnsupportedImageFormatError(Exception):
    """Exception raised for unsupported image formats."""

    def __init__(self, format: str):
        self.format = format
        self.message = f"Unsupported image format: {self.format}"
        super().__init__(self.message)


class DecodingError(Exception):
    """Exception raised for errors in decoding base64 images."""

    def __init__(self, message: str = "Failed to decode base64 image"):
        self.message = message
        super().__init__(self.message)
