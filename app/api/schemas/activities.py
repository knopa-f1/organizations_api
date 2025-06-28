from typing import Optional

from pydantic import ConfigDict, BaseModel


class ActivityCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None


class ActivityRead(ActivityCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

    # @classmethod
    # def from_orm_object(cls, orm_obj):
    #     data = {'id':orm_obj.id,
    #             'name':orm_obj.name,
    #             'building_id':orm_obj.building_id}
    #     return cls.model_validate(data)
