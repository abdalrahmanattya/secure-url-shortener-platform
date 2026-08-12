from datetime import UTC, datetime
from typing import Annotated

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator

from .validation import validate_destination

Code = Annotated[str, Field(min_length=6, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")]


class CreateLinkRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    destination: AnyHttpUrl = Field(max_length=2048)
    code: Code | None = None
    expires_at: datetime | None = Field(default=None, alias="expiresAt")

    @field_validator("destination")
    @classmethod
    def safe_destination(cls, value: AnyHttpUrl) -> AnyHttpUrl:
        validate_destination(str(value))
        return value

    @field_validator("expires_at")
    @classmethod
    def future_expiry(cls, value: datetime | None) -> datetime | None:
        if value is not None and value <= datetime.now(UTC):
            raise ValueError("expiresAt must be in the future")
        return value


class UpdateLinkRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")
    destination: AnyHttpUrl | None = Field(default=None, max_length=2048)
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    enabled: bool | None = None

    @field_validator("destination")
    @classmethod
    def safe_destination(cls, value: AnyHttpUrl | None) -> AnyHttpUrl | None:
        if value is not None:
            validate_destination(str(value))
        return value


class LinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    code: str
    short_url: str = Field(alias="shortUrl")
    destination: str
    created_at: datetime = Field(alias="createdAt")
    expires_at: datetime | None = Field(alias="expiresAt")
    enabled: bool
    status: str
    owner_id: str = Field(alias="ownerId")


class HealthResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    dependencies: dict[str, str]


class ErrorResponse(BaseModel):
    error: str
    message: str
    request_id: str = Field(alias="requestId")
