from sqlalchemy.orm import Session
from timestamp.db.models import Attendance
from datetime import datetime
from typing import Optional, Union, Tuple
from timestamp.schemas.attendance import Coordinates
from timestamp.core.config import env
import pytz


class AttendanceService:
    def __init__(
        self,
        db_session: Session,
    ):
        """Service for managing attendance records."""
        self.db_session = db_session

    def time_in(
        self,
        user_id: int,
        coordinates: Union[Coordinates, Tuple[float, float]],
        selfie: Optional[str] = None,
    ):
        """Record the time a user clocks in."""
        # Implementation to record time in for the user

        if self.is_user_clocked_in(user_id):
            raise Exception("User is already clocked in.")

        if isinstance(coordinates, Tuple):
            coordinates = Coordinates(latitude=coordinates[0], longitude=coordinates[1])

        attendance_record = Attendance(
            user_id=user_id,
            time_in=datetime.now(tz=pytz.timezone(env.TIMEZONE)),
            time_in_selfie=selfie,
            time_in_latitude=coordinates.latitude,
            time_in_longitude=coordinates.longitude,
        )
        self.db_session.add(attendance_record)
        self.db_session.commit()

    def time_out(
        self,
        user_id: int,
        coordinates: Union[Coordinates, Tuple[float, float]],
        selfie: Optional[str] = None,
    ):
        """Record the time a user clocks out."""
        # Implementation to record time out for the user
        if self.is_user_clocked_in(user_id):
            latest_attendance = self.get_latest_attendance(user_id)
            latest_attendance.time_out = datetime.now(tz=pytz.timezone(env.TIMEZONE))

            if isinstance(coordinates, Tuple):
                coordinates = Coordinates(
                    latitude=coordinates[0], longitude=coordinates[1]
                )
            latest_attendance.time_out_latitude = coordinates.latitude
            latest_attendance.time_out_longitude = coordinates.longitude
            latest_attendance.time_out_selfie = selfie
            self.db_session.commit()
        else:
            raise Exception("User is not currently clocked in.")

    def get_latest_attendance(self, user_id: int):
        """Get the latest attendance record for a user."""
        # Implementation to retrieve the latest attendance record for the user
        return (
            self.db_session.query(Attendance)
            .filter_by(user_id=user_id)
            .order_by(Attendance.time_in.desc())
            .first()
        )

    def is_user_clocked_in(self, user_id: int) -> bool:
        """Check if the user is currently clocked in."""
        latest_attendance = self.get_latest_attendance(user_id)
        return latest_attendance is not None and latest_attendance.time_out is None
