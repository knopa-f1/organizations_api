from pydantic import BaseModel, ConfigDict


class BuildingCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float


class BuildingRead(BuildingCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

