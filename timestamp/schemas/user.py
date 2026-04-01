from pydantic import BaseModel, Field
from typing import Optional


class UserMeResponse(BaseModel):
    email: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    role_id: str
    avatar_url: Optional[str]
    avatar_url_preview: Optional[str]


class UserCreateRequest(BaseModel):
    email: str
    password: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    # Refer to Role Enum in timestamp.schemas.enums.Role for valid role_id values
    role_id: int = Field(default=1, ge=1, le=3)


class UserUpdateEmailRequest(BaseModel):
    id: int
    email: str


class UserUpdatePasswordRequest(BaseModel):
    id: int
    old_password: str
    new_password: str


class UserUpdateAvatarRequest(BaseModel):
    id: int
    original_filename: str
    preview_filename: str


class UserUpdateRoleRequest(BaseModel):
    id: int
    # Refer to Role Enum in timestamp.schemas.enums.Role for valid role_id values
    role_id: int = Field(ge=1, le=3)
