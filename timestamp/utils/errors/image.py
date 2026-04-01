class UnsupportedImageFormatError(Exception):
    """Exception raised for unsupported image formats."""

    def __init__(self, format: str):
        self.format = format
        self.message = f"Unsupported image format: {self.format}"
        super().__init__(self.message)
