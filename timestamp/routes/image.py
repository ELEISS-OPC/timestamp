from fastapi import APIRouter, HTTPException, status

from timestamp.dependencies import AuthenticatedUser, Image_Service
from timestamp.schemas import image as image_schemas
from timestamp.schemas.annotations import ImageUpload
from timestamp.schemas.common import Detail
from timestamp.utils.errors import DecodingError
from timestamp.utils.validation import validate_role

router = APIRouter(prefix="/image", tags=["Image"])


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_403_FORBIDDEN: {"model": Detail}},
    response_model=image_schemas.ImageSet,
)
async def upload_image(
    authenticated_user: AuthenticatedUser,
    image_service: Image_Service,
    image: ImageUpload,
) -> image_schemas.ImageSet:
    """
    Upload images.

    Access Level: Admin, Officer, Employee
    """
    validate_role(authenticated_user.role_id, "oe")
    return image_service.upload_image(await image.read())


@router.post(
    "/base64",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_403_FORBIDDEN: {"model": Detail}},
    response_model=image_schemas.ImageSet,
)
async def upload_image_in_base64(
    authenticated_user: AuthenticatedUser,
    image_service: Image_Service,
    data: image_schemas.ImageUploadRequest,
) -> image_schemas.ImageSet:
    """
    Upload images.

    Access Level: Admin, Officer, Employee
    """
    validate_role(authenticated_user.role_id, "oe")

    try:
        return image_service.upload_image_base64(data.image)
    except DecodingError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to decode base64 image",
        )
