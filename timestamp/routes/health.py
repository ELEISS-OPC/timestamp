from fastapi import APIRouter

from timestamp.core.config import env

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
)
async def health_check():
    """
    Health check endpoint.

    Access Level: Public
    """
    return {
        "status": "healthy",
        "commit_hash": env.COMMIT_HASH,
        "version": env.VERSION,
    }
