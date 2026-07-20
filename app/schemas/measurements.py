from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class WeightIn(BaseModel):
    value_kg: float = Field(gt=20, lt=400)
    measured_at: datetime | None = None
    note: str | None = Field(default=None, max_length=500)


class WeightOut(BaseModel):
    id: int
    value_kg: float
    measured_at: datetime
    note: str | None
    source: str

    model_config = {"from_attributes": True}


class BloodPressureIn(BaseModel):
    systolic: int = Field(gt=40, lt=300)
    diastolic: int = Field(gt=20, lt=250)
    pulse: int | None = Field(default=None, gt=20, lt=250)
    measured_at: datetime | None = None
    note: str | None = Field(default=None, max_length=500)


class BloodPressureOut(BaseModel):
    id: int
    systolic: int
    diastolic: int
    pulse: int | None
    measured_at: datetime
    note: str | None
    source: str

    model_config = {"from_attributes": True}


class HeartRateIn(BaseModel):
    bpm: int = Field(gt=20, lt=250)
    context: Literal["resting", "active"] = "resting"
    measured_at: datetime | None = None
    note: str | None = Field(default=None, max_length=500)


class HeartRateOut(BaseModel):
    id: int
    bpm: int
    context: str
    measured_at: datetime
    note: str | None
    source: str

    model_config = {"from_attributes": True}


class GlucoseIn(BaseModel):
    value_mg_dl: float = Field(gt=20, lt=800)
    context: Literal["fasting", "after_meal", "random"] = "random"
    measured_at: datetime | None = None
    note: str | None = Field(default=None, max_length=500)


class GlucoseOut(BaseModel):
    id: int
    value_mg_dl: float
    context: str
    measured_at: datetime
    note: str | None
    source: str

    model_config = {"from_attributes": True}
