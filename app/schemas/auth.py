from datetime import datetime

from pydantic import BaseModel


class ApiKeyCreated(BaseModel):
    id: int
    name: str
    key_prefix: str
    raw_key: str  # pokazywany tylko raz, zaraz po utworzeniu


class ApiKeyOut(BaseModel):
    id: int
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: datetime | None

    model_config = {"from_attributes": True}
