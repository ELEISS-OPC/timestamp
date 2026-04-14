from datetime import datetime
from typing import Literal, Union, Optional

from pydantic import BaseModel, ConfigDict, Field

from .user import UserGetInfoResponse


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class TimeInRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user clocking in or out")
    coordinates: Coordinates
    selfie: str = Field(..., description="URL of the selfie image")
    selfie_preview: str = Field(..., description="URL of the selfie preview image")


class TimeOutRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user clocking in or out")
    coordinates: Coordinates
    selfie: str = Field(..., description="URL of the selfie image")
    selfie_preview: str = Field(..., description="URL of the selfie preview image")


class TimeInResponse(BaseModel):
    time_in: datetime = Field(..., description="The timestamp when the user clocked in")

    model_config = ConfigDict(from_attributes=True)


class TimeOutResponse(BaseModel):
    time_out: datetime = Field(
        ..., description="The timestamp when the user clocked out"
    )

    model_config = ConfigDict(from_attributes=True)


class TimeInAndOut(BaseModel):
    time_in: datetime = Field(..., description="The timestamp when the user clocked in")
    time_out: datetime = Field(
        ..., description="The timestamp when the user clocked out"
    )

    model_config = ConfigDict(from_attributes=True)


class AttendanceHistoryResponse(BaseModel):
    history: list[TimeInAndOut] = Field(
        ..., description="List of time in and out records for the user"
    )

    model_config = ConfigDict(from_attributes=True)


class CurrentStatusResponse(BaseModel):
    status: Union[Literal["timed_in"], Literal["timed_out"]] = Field(
        ..., description="Current status of the user (timed in or timed out)"
    )

    model_config = ConfigDict(from_attributes=True)


class DailyShiftTotalResponse(BaseModel):
    date: datetime = Field(
        ..., description="The date for which the total shifts are calculated"
    )
    total_shifts: int = Field(
        ..., description="Total number of shifts for the user on the current day"
    )

    model_config = ConfigDict(from_attributes=True)


class CompletedShiftsResponse(BaseModel):
    completed_shifts: list[DailyShiftTotalResponse] = Field(
        ...,
        description="List of total completed shifts for each day in the last 3 months",
    )

    model_config = ConfigDict(from_attributes=True)


class AttendanceRecordResponse(BaseModel):
    id: int = Field(..., description="ID of the attendance record")
    user: UserGetInfoResponse = Field(..., description="Information about the user")
    time_in: datetime = Field(..., description="The timestamp when the user clocked in")
    time_out: datetime = Field(
        ..., description="The timestamp when the user clocked out"
    )
    time_in_latitude: float = Field(
        ..., ge=-90, le=90, description="Latitude of time in location"
    )
    time_in_longitude: float = Field(
        ..., ge=-180, le=180, description="Longitude of time in location"
    )
    time_out_latitude: Optional[float] = Field(
        default=None, ge=-90, le=90, description="Latitude of time out location"
    )
    time_out_longitude: Optional[float] = Field(
        default=None, ge=-180, le=180, description="Longitude of time out location"
    )
    time_in_selfie: str = Field(..., description="URL of the time in selfie image")
    time_in_selfie_preview: str = Field(
        ..., description="URL of the time in selfie preview image"
    )
    time_out_selfie: Optional[str] = Field(
        default=None, description="URL of the time out selfie image"
    )
    time_out_selfie_preview: Optional[str] = Field(
        default=None, description="URL of the time out selfie preview image"
    )

    model_config = ConfigDict(from_attributes=True)
