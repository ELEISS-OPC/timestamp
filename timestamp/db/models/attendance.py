from typing import Optional

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, Default


class Attendance(Base, Default):
    """
    Attendance model representing an attendance record in the system.

    Attributes
    ----------
    id : int
        Primary key identifier for the attendance record.
    user_id : int
        Foreign key identifier for the user associated with the attendance record.
    time_in : TIMESTAMP
        Timestamp when the user clocked in.
    time_out : Optional[TIMESTAMP]
        Timestamp when the user clocked out. May be ``None`` if the user has not clocked out yet.
    time_in_selfie : str
        URL to the selfie taken when the user clocked in.
    time_out_selfie : Optional[str]
        URL to the selfie taken when the user clocked out. May be ``None`` if the user has not clocked out yet.
    time_in_latitude : float
        Latitude of the location where the user clocked in.
    time_in_longitude : float
        Longitude of the location where the user clocked in.
    time_out_latitude : Optional[float]
        Latitude of the location where the user clocked out. May be ``None`` if the user has not clocked out yet.
    time_out_longitude : Optional[float]
        Longitude of the location where the user clocked out. May be ``None`` if the user has not clocked out yet.
    """

    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    time_in: Mapped[TIMESTAMP] = mapped_column(nullable=False)
    time_out: Mapped[Optional[TIMESTAMP]] = mapped_column(nullable=True)
    time_in_selfie: Mapped[str] = mapped_column(nullable=False)
    time_out_selfie: Mapped[Optional[str]] = mapped_column(nullable=True)
    time_in_latitude: Mapped[float] = mapped_column(nullable=False)
    time_in_longitude: Mapped[float] = mapped_column(nullable=False)
    time_out_latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    time_out_longitude: Mapped[Optional[float]] = mapped_column(nullable=True)
