from typing import Annotated

from fastapi import Depends

from timestamp import services
from timestamp.core.config import env
from timestamp.schemas.auth import JWTConfig
from timestamp.schemas.enums import JWTAlgorithm

from .db import DB_Session


def get_user_service(
    db_session: DB_Session,
) -> services.UserService:
    return services.UserService(
        db_session,
        jwt_config=JWTConfig(
            secret_key=env.JWT_SECRET_KEY,
            algorithm=JWTAlgorithm(value=env.JWT_ALGORITHM),
            access_token_expire_minutes=env.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        ),
    )


def get_attendance_service(
    db_session: DB_Session,
) -> services.AttendanceService:
    return services.AttendanceService(db_session)


User_Service = Annotated[services.UserService, Depends(get_user_service)]
Attendance_Service = Annotated[
    services.AttendanceService, Depends(get_attendance_service)
]
