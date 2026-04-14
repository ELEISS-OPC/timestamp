from typing import Optional

from sqlalchemy import ForeignKey
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    time_in : datetime
        Timestamp when the user clocked in.
    time_out : Optional[datetime]
        Timestamp when the user clocked out. May be ``None`` if the user has not clocked out yet.
    time_in_selfie : str
        URL to the selfie taken when the user clocked in.
    time_in_selfie_preview : str
        URL to the preview of the selfie taken when the user clocked in.
    time_out_selfie_preview : Optional[str]
        URL to the preview of the selfie taken when the user clocked out. May be ``None`` if the user has not clocked out yet.
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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship()  # noqa: F821
    time_in: Mapped[datetime] = mapped_column(nullable=False)
    time_out: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    time_in_selfie: Mapped[str] = mapped_column(nullable=False)
    time_in_selfie_preview: Mapped[str] = mapped_column(nullable=True)
    time_out_selfie: Mapped[Optional[str]] = mapped_column(nullable=True)
    time_out_selfie_preview: Mapped[Optional[str]] = mapped_column(nullable=True)
    time_in_latitude: Mapped[float] = mapped_column(nullable=False)
    time_in_longitude: Mapped[float] = mapped_column(nullable=False)
    time_out_latitude: Mapped[Optional[float]] = mapped_column(nullable=True)
    time_out_longitude: Mapped[Optional[float]] = mapped_column(nullable=True)
