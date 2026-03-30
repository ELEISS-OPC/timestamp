from fastapi import APIRouter, status


router = APIRouter(tags=["Root"])


@router.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    """
    Root endpoint.

    Access Level: Public
    """
    return "Hello, from Timestamp!"
