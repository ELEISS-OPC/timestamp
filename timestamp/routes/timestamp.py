from fastapi import APIRouter, status, HTTPException

from timestamp.dependencies import Attendance_Service, AuthenticatedUser
from timestamp.schemas import attendance as attendance_schemas
from timestamp.schemas import Role, Detail
from timestamp.utils import errors
from timestamp.utils.validation import validate_role
from typing import Literal

router = APIRouter(prefix="/timestamp", tags=["Timestamp"])


@router.post(
    "/time-in",
    summary="Time In User",
    description="Time in the user and returns the current timestamp.",
    status_code=status.HTTP_200_OK,
    response_model=attendance_schemas.TimeInResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": Detail,
            "description": "User is already timed in.",
        },
        status.HTTP_404_NOT_FOUND: {"model": Detail, "description": "User not found."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": Detail,
            "description": "Internal server error.",
        },
    },
)
async def time_in(
    data: attendance_schemas.TimeInRequest,
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
    validate_role(user.role_id, "oe")
    if user.role_id in [Role.EMPLOYEE.value, Role.OFFICER.value] and (
        data.user_id != user.id
    ):
        raise errors.ForbiddenAccessError

    try:
        record = attendance_service.time_in(
            user_id=data.user_id,
            latitude=data.coordinates.latitude,
            longitude=data.coordinates.longitude,
            selfie=data.selfie,
        )
        return attendance_schemas.TimeInResponse.model_validate(record)
    except errors.AlreadyTimedInError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except (errors.UserNotFoundError, errors.NoRecordsFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while timing in the user.",
        ) from e


@router.put(
    "/time-out",
    summary="Time Out User",
    description="Time out the user and returns the current timestamp.",
    status_code=status.HTTP_200_OK,
    response_model=attendance_schemas.TimeOutResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": Detail,
            "description": "User is already timed out or hasn't timed in yet.",
        },
        status.HTTP_404_NOT_FOUND: {"model": Detail, "description": "User not found."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": Detail,
            "description": "Internal server error.",
        },
    },
)
async def time_out(
    data: attendance_schemas.TimeOutRequest,
    attendance_service: Attendance_Service,
    user: AuthenticatedUser,
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
    validate_role(user.role_id, "oe")
    if user.role_id in [Role.EMPLOYEE.value, Role.OFFICER.value] and (
        data.user_id != user.id
    ):
        raise errors.ForbiddenAccessError

    try:
        record = attendance_service.time_out(
            user_id=data.user_id,
            latitude=data.coordinates.latitude,
            longitude=data.coordinates.longitude,
            selfie=data.selfie,
        )
        return attendance_schemas.TimeOutResponse.model_validate(record)
    except errors.AlreadyTimedOutError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except (errors.UserNotFoundError, errors.NoRecordsFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while timing out the user.",
        ) from e


@router.get(
    "/current-status/{user_id}",
    summary="Current Status of User",
    description="Returns the current status of the user (timed in or timed out).",
    status_code=status.HTTP_200_OK,
    response_model=attendance_schemas.CurrentStatusResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": Detail,
            "description": "Forbidden access to view the current status of the user.",
        },
        status.HTTP_404_NOT_FOUND: {"model": Detail, "description": "User not found."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": Detail,
            "description": "Internal server error.",
        },
    },
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
    validate_role(user.role_id, "oe")
    if user.role_id in [Role.EMPLOYEE.value] and (user_id != user.id):
        raise errors.ForbiddenAccessError

    try:
        status_str = attendance_service.current_status(user_id)
        return attendance_schemas.CurrentStatusResponse(status=status_str)
    except errors.NoRecordsFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the current status of the user.",
        ) from e


@router.get(
    "/attendance-history/{user_id}",
    summary="Attendance History of User",
    description="Returns the attendance history of the user.",
    status_code=status.HTTP_200_OK,
    response_model=attendance_schemas.AttendanceHistoryResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": Detail,
            "description": "Forbidden access to view the time in history of the user.",
        },
        status.HTTP_404_NOT_FOUND: {"model": Detail, "description": "User not found."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": Detail,
            "description": "Internal server error.",
        },
    },
)
async def attendance_history(
    user_id: int, attendance_service: Attendance_Service, user: AuthenticatedUser
):
    """
    Returns the attendance history of the user.

    Access Level: Employee, Officer, Admin

    Raises:
        HTTPException: If the user is not found.
        HTTPException: If the user is not authenticated.
        HTTPException: If the user is not authorized to view the attendance history.
    """
    validate_role(user.role_id, "oe")
    if user.role_id in [Role.EMPLOYEE.value] and (user_id != user.id):
        raise errors.ForbiddenAccessError
    try:
        records = attendance_service.time_in_history(user_id)
        return attendance_schemas.AttendanceHistoryResponse(history=records)
    except errors.NoRecordsFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the time in history of the user.",
        ) from e


@router.get(
    "/analytics/completed-shifts",
    summary="Get Completed Shifts Timeseries",
    description="Returns a daily count of completed shifts for the last 3 months. Restricted to Admins and Officers.",
    status_code=status.HTTP_200_OK,
    # response_model=attendance_schemas.CompletedShiftsSeriesResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": Detail,
            "description": "Not authorized to view analytics.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": Detail,
            "description": "Internal server error.",
        },
    },
)
async def get_attendance_analytics(
    attendance_service: Attendance_Service, user: AuthenticatedUser
):
    """
    Returns the daily volume of completed shifts for the organization.

    Access Level: Officer, Admin
    """
    validate_role(user.role_id, "o")

    try:
        data = attendance_service.get_completed_shifts_recent_history()
        return attendance_schemas.CompletedShiftsResponse(
            completed_shifts=[
                attendance_schemas.DailyShiftTotalResponse(
                    date=record["date"], total_shifts=record["total_shifts"]
                )
                for record in data
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching analytics data.",
        ) from e


@router.get(
    "/analytics/bradford-aggregate",
    summary="Get Aggregate Bradford Score",
    description="Returns the median, average, minimum, or maximum Bradford Score across all users.",
)
async def get_bradford_analytics(
    aggregate: Literal["median", "average", "minimum", "maximum"],
    attendance_service: Attendance_Service,
    user: AuthenticatedUser,
):
    """
    Returns the requested aggregate statistic for the organization's Bradford Scores.

    Access Level: Officer, Admin
    """
    # Restrict to Officers/Admins
    validate_role(user.role_id, "o")

    try:
        result = attendance_service.get_bradford_summary(aggregate)
        return {
            "aggregate_type": aggregate,
            "value": round(result, 2),
            "metric": "Bradford Factor",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate Bradford aggregate: {str(e)}",
        )
