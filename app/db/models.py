from sqlalchemy import String, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.schemas.activities import ActivityRead
from app.api.schemas.buildings import BuildingRead
from app.api.schemas.organizations import OrganizationDetailRead
from app.db.database import Base

organization_activities = Table(
    "organization_activities",
    Base.metadata,
    Column("organization_id", ForeignKey("organization.id")),
    Column("activity_id", ForeignKey("activity.id")),
)


class Building(Base): # pylint: disable=too-few-public-methods
    __tablename__ = "building"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)
    latitude: Mapped[float]
    longitude: Mapped[float]

    organizations = relationship("Organization", back_populates="building")

    def to_pydantic_model(self) -> BuildingRead:
        return BuildingRead(
            id=self.id,
            name=self.name,
            address=self.address,
            latitude=self.latitude,
            longitude=self.longitude
        )


class Activity(Base): # pylint: disable=too-few-public-methods
    __tablename__ = "activity"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("activity.id"), nullable=True)

    parent: Mapped['Activity'] = relationship(
        "Activity",
        remote_side=[id],
        back_populates="children"
    )

    children: Mapped[list['Activity']] = relationship(
        "Activity",
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    def to_pydantic_model(self) -> ActivityRead:
        return ActivityRead(
            id=self.id,
            name=self.name,
            parent_id=self.parent_id
        )


class Organization(Base): # pylint: disable=too-few-public-methods
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    building_id: Mapped[int] = mapped_column(ForeignKey("building.id"))

    building = relationship("Building", back_populates="organizations")
    phones = relationship("Phone", back_populates="organization", cascade="all, delete-orphan")
    activities = relationship("Activity", secondary=organization_activities, backref="organizations")

    def to_pydantic_model(self) -> OrganizationDetailRead:
        return OrganizationDetailRead(
            id=self.id,
            name=self.name,
            building_id=self.building_id,
            phones=[phone.number for phone in self.phones],
            activities=[Activity.to_pydantic_model(activity) for activity in self.activities]
        )


class Phone(Base): # pylint: disable=too-few-public-methods
    __tablename__ = "phone"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"))

    organization = relationship("Organization", back_populates="phones")
