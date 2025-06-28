from typing import List

from pydantic import BaseModel, ConfigDict

from app.api.schemas.activities import ActivityRead


class OrganizationPhone(BaseModel):
    phone: str


class OrganizationCreate(BaseModel):
    name: str
    building_id: int
    phones: List[str]
    activity_ids: List[int]


class OrganizationRead(BaseModel):
    id: int
    name: str
    building_id: int

    model_config = ConfigDict(from_attributes=True)


class OrganizationDetailRead(OrganizationRead):
    phones: list[str]
    activities: list[ActivityRead]

    model_config = ConfigDict(from_attributes=True)
