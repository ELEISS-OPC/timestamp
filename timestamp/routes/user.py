from fastapi import APIRouter, HTTPException, status

from timestamp.db.models import User
from timestamp.dependencies import AuthenticatedUser, User_Service
from timestamp.schemas import user as user_schemas
from timestamp.schemas.common import Detail
from timestamp.schemas.enums import Role
from timestamp.utils import errors
from timestamp.utils.validation import validate_role

router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.UserMeResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": Detail}},
)
async def get_user(
    user_service: User_Service, authenticated_user: AuthenticatedUser
) -> user_schemas.UserMeResponse:
    """
    Get a user's own information.

    Access Level: Employee, Officer, Admin
    """
    try:
        user: User = user_service.get_user(email=authenticated_user.email)
        return user_schemas.UserMeResponse.model_validate(user)
    except errors.UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=user_schemas.UserCreateResponse,
    responses={status.HTTP_409_CONFLICT: {"model": Detail}},
)
async def create_user(
    user: user_schemas.UserCreateRequest,
    user_service: User_Service,
    authenticated_user: AuthenticatedUser,
) -> user_schemas.UserCreateResponse:
    """
    Create a new user.

    Access Level: Officer, Admin
    """
    validate_role(authenticated_user.role_id, "o")
    try:
        new_user: User = user_service.create_user(
            email=user.email,
            password=user.password,
            first_name=user.first_name,
            middle_name=user.middle_name,
            last_name=user.last_name,
            role=Role(user.role_id),
        )
        return user_schemas.UserCreateResponse.model_validate(new_user)
    except errors.UserExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=Detail,
    responses={status.HTTP_404_NOT_FOUND: {"model": Detail}},
)
async def delete_user(
    user_id: int, user_service: User_Service, authenticated_user: AuthenticatedUser
) -> Detail:
    """
    Delete a user by ID.

    Access Level: Officer, Admin
    """
    validate_role(authenticated_user.role_id, "o")

    try:
        user_to_delete = user_service.get_user(user_id=user_id)

        # Officers cannot delete admins
        if (authenticated_user.role_id == Role.OFFICER) and (
            user_to_delete.role_id == Role.ADMIN
        ):
            raise errors.ForbiddenAccessError

        # Officers cannot delete accounts of other officers
        if (authenticated_user.role_id == Role.OFFICER) and (
            user_to_delete.role_id == Role.OFFICER
        ):
            if authenticated_user.id != user_to_delete.id:
                raise errors.ForbiddenAccessError

        user_service.delete_user(user_id=user_id)

        return Detail(detail=f"User with ID {user_id} has been deleted.")
    except errors.UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.put(
    "/email",
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.UserUpdateEmailRequest,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Detail},
        status.HTTP_404_NOT_FOUND: {"model": Detail},
        status.HTTP_409_CONFLICT: {"model": Detail},
    },
)
async def update_user_email(
    user: user_schemas.UserUpdateEmailRequest,
    user_service: User_Service,
    authenticated_user: AuthenticatedUser,
) -> user_schemas.UserUpdateEmailRequest:
    """
    Update user email.

    Access Level: Officer, Admin
    """
    validate_role(authenticated_user.role_id, "o")
    try:
        user_to_update = user_service.get_user(user_id=user.id)

        # Officers can only update their own email and employees
        if (authenticated_user.role_id == Role.OFFICER) and (
            user_to_update.role_id == Role.ADMIN
        ):
            raise errors.ForbiddenAccessError

        # Officers cannot update emails of other officers
        if (authenticated_user.role_id == Role.OFFICER) and (
            user_to_update.role_id == Role.OFFICER
        ):
            if authenticated_user.id != user_to_update.id:
                raise errors.ForbiddenAccessError

        updated_user: User = user_service.update_user_email(
            user_id=user.id, new_email=user.email
        )
        return user_schemas.UserUpdateEmailRequest.model_validate(updated_user)
    except errors.UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except errors.UserExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.put(
    "/password",
    status_code=status.HTTP_200_OK,
    response_model=Detail,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Detail},
        status.HTTP_404_NOT_FOUND: {"model": Detail},
    },
)
async def update_user_password(
    user: user_schemas.UserUpdatePasswordRequest,
    user_service: User_Service,
    authenticated_user: AuthenticatedUser,
) -> Detail:
    """
    Update user password.

    Access Level: Employee, Officer, Admin (users can only update their own password)
    """
    validate_role(authenticated_user.role_id, "all")
    try:
        user_to_update = user_service.get_user(user_id=user.id)

        # Officers and Employees can only update their own password and cannot update passwords of other officers or admins
        if (
            authenticated_user.role_id != Role.ADMIN
            and authenticated_user.id != user_to_update.id
        ):
            raise errors.ForbiddenAccessError

        # Admins can update any user's password, but cannot update passwords of other admins
        if (
            authenticated_user.role_id == Role.ADMIN
            and user_to_update.role_id == Role.ADMIN
        ):
            if authenticated_user.id != user_to_update.id:
                raise errors.ForbiddenAccessError

        user_service.update_user_password(
            user_id=user.id,
            old_password=user.old_password,
            new_password=user.new_password,
        )
        return Detail(detail=f"Password for user with ID {user.id} has been updated.")
    except errors.InvalidPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except errors.UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.put(
    "/img",
    status_code=status.HTTP_200_OK,
    response_model=Detail,
)
async def update_user_img(
    user: user_schemas.UserUpdateAvatarRequest,
    user_service: User_Service,
    authenticated_user: AuthenticatedUser,
):
    """
    Update the current user's profile.

    Access Level: Admin, User
    """
    validate_role(authenticated_user.role_id, "all")
    try:
        user_to_update = user_service.get_user(user_id=user.id)

        # Officers and Employees can only update their own avatar and cannot update avatars of other officers or admins
        if (
            authenticated_user.role_id != Role.ADMIN
            and authenticated_user.id != user_to_update.id
        ):
            raise errors.ForbiddenAccessError

        # Admins can update any user's avatar, but cannot update avatars of other admins
        if (
            authenticated_user.role_id == Role.ADMIN
            and user_to_update.role_id == Role.ADMIN
        ):
            if authenticated_user.id != user_to_update.id:
                raise errors.ForbiddenAccessError

        user_service.update_user_img(
            user_id=user.id,
            img=user.original_filename,
            preview_img=user.preview_filename,
        )
        return Detail(detail=f"Avatar for user with ID {user.id} has been updated.")

    except errors.UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.put(
    "/role/",
    status_code=status.HTTP_200_OK,
)
async def change_user_role(
    user: user_schemas.UserUpdateRoleRequest,
    user_service: User_Service,
    authenticated_user: AuthenticatedUser,
):
    """
    Change a user's role between Employee and Officer.
    Admin accounts cannot have their role changed nor can any account be changed to Admin.

    Access Level: Admin
    """
    validate_role(authenticated_user.role_id, "a")
    try:
        user_to_update = user_service.get_user(user_id=user.id)

        # No role changes allowed for admins, whether promotion/demotion or self-demotion
        if user_to_update.role_id == Role.ADMIN:
            raise errors.ForbiddenAccessError

        # No one can be promoted to admin
        if user.role_id == Role.ADMIN:
            raise errors.ForbiddenAccessError

        user_service.change_user_role(user_id=user.id, role_id=user.role_id)
        return Detail(
            detail=f"Role for user with ID {user.id} has been updated to {Role(user.role_id).name}."
        )
    except errors.UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
