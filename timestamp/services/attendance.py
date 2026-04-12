import statistics
from datetime import datetime
from typing import Literal, Optional, Union

import pytz
from dateutil.relativedelta import relativedelta
from psycopg2.errors import ForeignKeyViolation  # type: ignore[attr-defined]
from sqlalchemy import exc, extract, func
from sqlalchemy.orm import Session

from timestamp.core.config import env
from timestamp.db.models import Attendance, User
from timestamp.utils import errors


class AttendanceService:
    def __init__(
        self,
        db_session: Session,
    ):
        """
        Initialize the attendance service.

        Parameters
        ----------
        db_session : Session
            Active SQLAlchemy session used for attendance persistence.
        """
        self.db_session = db_session

    def time_in(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
        selfie: Optional[str] = None,
        selfie_preview: Optional[str] = None,
    ):
        """
        Record a time-in event for a user.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user clocking in.
        latitude : float
            Latitude where the time-in was recorded.
        longitude : float
            Longitude where the time-in was recorded.
        selfie : Optional[str], optional
            URL for the time-in selfie, by default None.
        selfie_preview : Optional[str], optional
            URL for the time-in selfie preview, by default None.


        Returns
        -------
        Attendance
            The created attendance record.

        Raises
        ------
        AlreadyTimedInError
            If the latest record for the user is still open.
        """

        try:
            if self.is_user_clocked_in(user_id):
                raise errors.AlreadyTimedInError(user_id=user_id)
        except errors.NoRecordsFoundError:
            pass  # No records found, so the user is not clocked in

        try:
            attendance_record = Attendance(
                user_id=user_id,
                time_in=datetime.now(tz=pytz.timezone(env.TIMEZONE)),
                time_in_selfie=selfie,
                time_in_selfie_preview=selfie_preview,
                time_in_latitude=latitude,
                time_in_longitude=longitude,
            )

            self.db_session.add(attendance_record)
            self.db_session.commit()

            return attendance_record
        except exc.IntegrityError as e:
            self.db_session.rollback()

            if isinstance(e.orig, ForeignKeyViolation):
                raise errors.UserNotFoundError(user_id=user_id)

            raise e

    def time_out(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
        selfie: Optional[str] = None,
        selfie_preview: Optional[str] = None,
    ):
        """
        Record a time-out event for a user.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user clocking out.
        latitude : float
            Latitude where the time-out was recorded.
        longitude : float
            Longitude where the time-out was recorded.
        selfie : Optional[str], optional
            URL for the time-out selfie, by default None.
        selfie_preview : Optional[str], optional
            URL for the time-out selfie preview, by default None.


        Returns
        -------
        Attendance
            The updated attendance record containing time-out details.

        Raises
        ------
        AlreadyTimedOutError
            If there is no open attendance record to close.
        """
        if self.is_user_clocked_in(user_id):
            latest_attendance = self.get_latest_attendance(user_id)
            latest_attendance.time_out = datetime.now(tz=pytz.timezone(env.TIMEZONE))

            latest_attendance.time_out_latitude = latitude
            latest_attendance.time_out_longitude = longitude
            latest_attendance.time_out_selfie = selfie
            latest_attendance.time_out_selfie_preview = selfie_preview
        else:
            self.db_session.rollback()
            raise errors.AlreadyTimedOutError(user_id=user_id)
        try:
            self.db_session.commit()
            return latest_attendance
        except exc.IntegrityError as e:
            self.db_session.rollback()

            if isinstance(e.orig, ForeignKeyViolation):
                raise errors.UserNotFoundError(user_id=user_id)

            raise e

    def get_latest_attendance(self, user_id: int):
        """
        Retrieve the most recent attendance record for a user.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.

        Returns
        -------
        Attendance
            The latest attendance record ordered by newest time-in.

        Raises
        ------
        NoRecordsFoundError
            If the user has no attendance records.
        """
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
        """
        Determine whether a user currently has an open attendance record.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.

        Returns
        -------
        bool
            True when the latest attendance record has no time-out, otherwise False.

        Raises
        ------
        NoRecordsFoundError
            If the user has no attendance records.
        """
        try:
            latest_attendance = self.get_latest_attendance(user_id)
            return latest_attendance.time_out is None
        except errors.NoRecordsFoundError:
            if self.does_user_exist(user_id):
                return False
            raise errors.UserNotFoundError(user_id=user_id)

    def does_user_exist(self, user_id: int) -> bool:
        """
        Check if a user exists.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.

        Returns
        -------
        bool
            True if the user exists, otherwise False.
        """
        return self.db_session.query(User).filter_by(id=user_id).first() is not None

    def current_status(
        self, user_id: int
    ) -> Union[Literal["timed_in"], Literal["timed_out"]]:
        """
        Return the user's current attendance status.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.

        Returns
        -------
        Literal["timed_in"] | Literal["timed_out"]
            "timed_in" when the user has an open attendance entry,
            otherwise "timed_out".

        Raises
        ------
        NoRecordsFoundError
            If the user has no attendance records.
        """
        if self.is_user_clocked_in(user_id):
            return "timed_in"
        return "timed_out"

    def time_in_history(self, user_id: int):
        """
        Retrieve complete attendance history for a user.

        Parameters
        ----------
        user_id : int
            Unique identifier of the user.

        Returns
        -------
        list[Attendance]
            Attendance records ordered from oldest to newest by time-in.

        Raises
        ------
        NoRecordsFoundError
            If the user has no attendance records.
        """
        attendance_records = (
            self.db_session.query(Attendance)
            .filter_by(user_id=user_id)
            .order_by(Attendance.time_in.asc())
            .all()
        )

        if not attendance_records:
            raise errors.NoRecordsFoundError(user_id=user_id)

        return attendance_records

    def get_completed_shifts_recent_history(self):
        """
        Get a timeseries of total completed shifts across all users,
        bounded by the last 3 months up to the current day.

        Returns
        -------
        list[dict]
            A list of dictionaries with the date and the total count.
        """
        # 1. Calculate the date range
        # We use the current time in the configured timezone
        now = datetime.now(tz=pytz.timezone(env.TIMEZONE))
        three_months_ago = now - relativedelta(months=3)

        # 2. Build the query with date boundaries
        query = (
            self.db_session.query(
                func.date(Attendance.time_in).label("shift_date"),
                func.count(Attendance.id).label("total_shifts"),
            )
            .filter(Attendance.time_out.isnot(None))
            .filter(Attendance.time_in >= three_months_ago)
            .filter(Attendance.time_in <= now)
            .group_by("shift_date")
            .order_by("shift_date")
        )

        results = query.all()

        # 3. Format results
        return [
            {"date": row.shift_date, "total_shifts": row.total_shifts}
            for row in results
        ]

    def get_bradford_summary(
        self, aggregate: Literal["median", "average", "minimum", "maximum", "sum"]
    ):
        """
        Calculates the Bradford Factor for all users and returns the
        requested aggregate statistic. The lower the score, the better, as it indicates fewer and less severe absences.

        Formula: B = S² * D
        S = Total number of separate absence spells
        D = Total number of days of absence

        Parameters
        ----------
        aggregate : Literal["median", "average", "minimum", "maximum", "sum"]
            The type of aggregate statistic to return for the Bradford Scores.

        Returns
        -------
        float
            The calculated aggregate Bradford Score across all users.
        """

        # 1. Calculate duration in decimal days for each record (PostgreSQL syntax)
        # 86400 is the number of seconds in a day.
        duration_days = (
            extract("epoch", Attendance.time_out - Attendance.time_in) / 86400
        )

        user_stats = (
            self.db_session.query(
                Attendance.user_id,
                func.count(Attendance.id).label("spells"),
                func.sum(duration_days).label("total_days"),
            )
            .filter(Attendance.time_out.isnot(None))
            .group_by(Attendance.user_id)
            .all()
        )

        if not user_stats:
            return 0

        # 2. Calculate the Bradford Score per user: (S^2) * D
        scores = [(row.spells**2) * (row.total_days or 0) for row in user_stats]

        # 3. Mapping the requested Aggregate Function
        stats_map = {
            "average": lambda x: sum(x) / len(x),
            "median": statistics.median,
            "minimum": min,
            "maximum": max,
            "sum": sum,
        }

        if aggregate not in stats_map:
            raise ValueError(f"Unsupported aggregate type: {aggregate}")

        return stats_map[aggregate](scores)
