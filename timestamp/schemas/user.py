from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class UserMeResponse(BaseModel):
    id: int
    email: str
    first_name: str
    middle_name: Optional[str] = Field(default=None)
    last_name: str
    role_id: int
    avatar_url: Optional[str] = Field(default=None)
    avatar_url_preview: Optional[str] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseModel):
    email: str
    password: str
    first_name: str
    middle_name: Optional[str] = Field(default=None)
    last_name: str
    # Refer to Role Enum in timestamp.schemas.enums.Role for valid role_id values
    role_id: int = Field(
        default=1,
        ge=1,
        le=2,
        description="Only Employee (1) or Officer (2) roles can be assigned via this endpoint.",
    )

    model_config = ConfigDict(from_attributes=True)


class UserCreateResponse(BaseModel):
    id: int
    email: str
    first_name: str
    middle_name: Optional[str] = Field(default=None)
    last_name: str
    role_id: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdateEmailRequest(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdatePasswordRequest(BaseModel):
    id: int
    old_password: str
    new_password: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdateAvatarRequest(BaseModel):
    id: int
    original_filename: str
    preview_filename: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdateRoleRequest(BaseModel):
    id: int
    # Refer to Role Enum in timestamp.schemas.enums.Role for valid role_id values
    role_id: int = Field(
        ge=1,
        le=2,
        description="Only Employee (1) or Officer (2) roles can be assigned via this endpoint.",
    )

    model_config = ConfigDict(from_attributes=True)
