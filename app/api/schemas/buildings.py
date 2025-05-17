from pydantic import BaseModel, ConfigDict


class BuildingCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float


class BuildingRead(BuildingCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

    # @classmethod
    # def from_orm_object(cls, orm_obj):
    #     data = {'id':orm_obj.id,
    #             'name': orm_obj.name,
    #             'address': orm_obj.address,
    #             'latitude': orm_obj.latitude,
    #             'longitude': orm_obj.longitude}
    #     return cls.model_validate(data)
