"""Database tables and API schemas."""

from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

Weekday = Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


class ProfileBase(SQLModel):
    name: str
    goal: str | None = None  # free text, e.g. "Half marathon under 2h"
    weekly_km: float | None = Field(default=None, ge=0)
    days_per_week: int | None = Field(default=None, ge=1, le=7)
    blocked_weekdays: list[Weekday] = Field(default_factory=list, sa_column=Column(JSON))


class UserProfile(ProfileBase, table=True):
    __tablename__ = "user_profile"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProfileCreate(ProfileBase):
    pass


class ProfileRead(ProfileBase):
    id: int
    created_at: datetime


class ProfileUpdate(SQLModel):
    """All fields optional: only the ones sent are changed."""

    name: str | None = None
    goal: str | None = None
    weekly_km: float | None = Field(default=None, ge=0)
    days_per_week: int | None = Field(default=None, ge=1, le=7)
    blocked_weekdays: list[Weekday] | None = None
