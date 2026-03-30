from fastapi import APIRouter, status

router = APIRouter(prefix="/timestamp", tags=["Timestamp"])


@router.get(
    "/time-in/{user_id}",
    summary="Time In User",
    description="Time in the user and returns the current timestamp.",
    status_code=status.HTTP_200_OK,
)
async def time_in(user_id: int):
    """
    Time in the user and returns the current timestamp=.

    Access Level: Employee

    Raises:
        HTTPException: If the user is already timed in.
        HTTPException: If there is an error while timing in the user.
        HTTPException: If the user is not found.
        HTTPException: If the user is not authenticated.
        HTTPException: If the user is not authorized to time in.
    """
    pass


@router.get(
    "/time-out/{user_id}",
    summary="Time Out User",
    description="Time out the user and returns the current timestamp.",
    status_code=status.HTTP_200_OK,
)
async def time_out(user_id: int):
    """
    Time out the user and returns the current timestamp.

    Access Level: Employee

    Raises:
        HTTPException: If the user is already timed out.
        HTTPException: If there is an error while timing out the user.
        HTTPException: If the user is not found.
        HTTPException: If the user is not authenticated.
        HTTPException: If the user is not authorized to time out.
    """
    pass


@router.get(
    "/current-status/{user_id}",
    summary="Current Status of User",
    description="Returns the current status of the user (timed in or timed out).",
    status_code=status.HTTP_200_OK,
)
async def current_status(user_id: int):
    """
    Returns the current status of the user (timed in or timed out).

    Access Level: Employee

    Raises:
        HTTPException: If the user is not found.
        HTTPException: If the user is not authenticated.
        HTTPException: If the user is not authorized to view the current status.
    """


@router.get(
    "/time-in-history/{user_id}",
    summary="Time In History of User",
    description="Returns the time in history of the user.",
    status_code=status.HTTP_200_OK,
)
async def time_in_history(user_id: int):
    """
    Returns the time in history of the user.

    Access Level: Employee

    Raises:
        HTTPException: If the user is not found.
        HTTPException: If the user is not authenticated.
        HTTPException: If the user is not authorized to view the time in history.
    """
    pass
