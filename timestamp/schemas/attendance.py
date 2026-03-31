from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
