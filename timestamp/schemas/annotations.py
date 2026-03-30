from typing import Annotated

from annotated_types import Len, MinLen
from fastapi import File, UploadFile
from pydantic import AfterValidator

from timestamp.utils.validation import validate_password, validate_version

CommitHash = str
Username = Annotated[str, MinLen(3)]
Password = Annotated[
    str, Len(min_length=8, max_length=128), AfterValidator(validate_password)
]  # Unhashed password
Version = Annotated[str, MinLen(5), AfterValidator(validate_version)]
ImageUpload = Annotated[UploadFile, File()]
