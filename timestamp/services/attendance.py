from sqlalchemy.orm import Session
from timestamp.db.models import Attendance
from datetime import datetime
from typing import Optional
from timestamp.core.config import env
from timestamp.utils import errors
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
        latitude: float,
        longitude: float,
        selfie: Optional[str] = None,
    ):
        """Record the time a user clocks in."""

        try:
            if self.is_user_clocked_in(user_id):
                raise errors.AlreadyTimedInError(user_id=user_id)
        except errors.NoRecordsFoundError:
            pass  # No records found, so the user is not clocked in

        attendance_record = Attendance(
            user_id=user_id,
            time_in=datetime.now(tz=pytz.timezone(env.TIMEZONE)),
            time_in_selfie=selfie,
            time_in_latitude=latitude,
            time_in_longitude=longitude,
        )
        self.db_session.add(attendance_record)
        self.db_session.commit()

        return attendance_record

    def time_out(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
        selfie: Optional[str] = None,
    ):
        """Record the time a user clocks out."""
        # Implementation to record time out for the user
        if self.is_user_clocked_in(user_id):
            latest_attendance = self.get_latest_attendance(user_id)
            latest_attendance.time_out = datetime.now(tz=pytz.timezone(env.TIMEZONE))

            latest_attendance.time_out_latitude = latitude
            latest_attendance.time_out_longitude = longitude
            latest_attendance.time_out_selfie = selfie
        else:
            self.db_session.rollback()
            raise errors.AlreadyTimedOutError(user_id=user_id)

        self.db_session.commit()
        return latest_attendance

    def get_latest_attendance(self, user_id: int):
        """Get the latest attendance record for a user."""
        # Implementation to retrieve the latest attendance record for the user
        attendance_record = (
            self.db_session.query(Attendance)
            .filter_by(user_id=user_id)
            .order_by(Attendance.time_in.desc())
            .first()
        )

        if attendance_record is None:
            raise errors.NoRecordsFoundError(user_id=user_id)
        return attendance_record

    def is_user_clocked_in(self, user_id: int) -> bool:
        """Check if the user is currently clocked in."""
        latest_attendance = self.get_latest_attendance(user_id)
        return latest_attendance is not None and latest_attendance.time_out is None
