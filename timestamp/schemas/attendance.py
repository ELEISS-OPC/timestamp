from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Union


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class TimeInRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user clocking in or out")
    coordinates: Coordinates
    selfie: str = Field(..., description="Base64-encoded selfie image")


class TimeOutRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user clocking in or out")
    coordinates: Coordinates
    selfie: str = Field(..., description="Base64-encoded selfie image")


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
