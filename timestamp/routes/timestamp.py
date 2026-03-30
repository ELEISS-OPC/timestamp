from fastapi import APIRouter, status

from timestamp.dependencies import Attendance_Service, AuthenticatedUser
from timestamp.utils import errors
from timestamp.utils.validation import validate_role
from timestamp.schemas.enums import Role

router = APIRouter(prefix="/timestamp", tags=["Timestamp"])


@router.get(
    "/time-in/{user_id}",
    summary="Time In User",
    description="Time in the user and returns the current timestamp.",
    status_code=status.HTTP_200_OK,
)
async def time_in(
    user_id: int,
    attendance_service: Attendance_Service,
    user: AuthenticatedUser,
):
    """
    Time in the user and returns the current timestamp=.

    Access Level: Employee, Officer, Admin

    Raises:
        HTTPException: If the user is already timed in.
        HTTPException: If there is an error while timing in the user.
        HTTPException: If the user is not found.
        HTTPException: If the user is not authenticated.
        HTTPException: If the user is not authorized to time in.
    """
    validate_role(user.role, "oe")
    if user.role in [Role.EMPLOYEE.value, Role.OFFICER.value] and (user_id != user.id):
        raise errors.ForbiddenAccessError

    return {"message": "ok"}


@router.get(
    "/time-out/{user_id}",
    summary="Time Out User",
    description="Time out the user and returns the current timestamp.",
    status_code=status.HTTP_200_OK,
)
async def time_out(
    user_id: int, attendance_service: Attendance_Service, user: AuthenticatedUser
):
    """
    Time out the user and returns the current timestamp.

    Access Level: Employee, Officer, Admin

    Raises:
        HTTPException: If the user is already timed out.
        HTTPException: If there is an error while timing out the user.
        HTTPException: If the user is not found.
        HTTPException: If the user is not authenticated.
        HTTPException: If the user is not authorized to time out.
    """
    validate_role(user.role, "oe")
    if user.role in [Role.EMPLOYEE.value, Role.OFFICER.value] and (user_id != user.id):
        raise errors.ForbiddenAccessError

    return {"message": "ok"}


@router.get(
    "/current-status/{user_id}",
    summary="Current Status of User",
    description="Returns the current status of the user (timed in or timed out).",
    status_code=status.HTTP_200_OK,
)
async def current_status(
    user_id: int, attendance_service: Attendance_Service, user: AuthenticatedUser
):
    """
    Returns the current status of the user (timed in or timed out).

    Access Level: Employee, Officer, Admin

    Raises:
        HTTPException: If the user is not found.
        HTTPException: If the user is not authenticated.
        HTTPException: If the user is not authorized to view the current status.
    """
    validate_role(user.role, "oe")
    if user.role in [Role.EMPLOYEE.value] and (user_id != user.id):
        raise errors.ForbiddenAccessError

    return {"message": "ok"}


@router.get(
    "/time-in-history/{user_id}",
    summary="Time In History of User",
    description="Returns the time in history of the user.",
    status_code=status.HTTP_200_OK,
)
async def time_in_history(
    user_id: int, attendance_service: Attendance_Service, user: AuthenticatedUser
):
    """
    Returns the time in history of the user.

    Access Level: Employee

    Raises:
        HTTPException: If the user is not found.
        HTTPException: If the user is not authenticated.
        HTTPException: If the user is not authorized to view the time in history.
    """
    validate_role(user.role, "oe")
    if user.role in [Role.EMPLOYEE.value] and (user_id != user.id):
        raise errors.ForbiddenAccessError

    return {"message": "ok"}
