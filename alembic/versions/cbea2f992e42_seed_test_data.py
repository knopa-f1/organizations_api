"""seed test data

Revision ID: cbea2f992e42
Revises: 70c0605267a5
Create Date: 2025-06-28 17:56:20.189600

"""
from typing import Sequence, Union

from alembic import op

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Activity, Building, Organization, Phone

# revision identifiers, used by Alembic.
revision: str = 'cbea2f992e42'
down_revision: Union[str, None] = '70c0605267a5'
branch_labels: Union[str, Sequence[str], None] = ('seed_data',)
depends_on: Union[str, Sequence[str], None] = '70c0605267a5'


def upgrade():
    if settings.MODE != "TEST":
        return

    bind = op.get_bind()
    session = Session(bind=bind)

    food = Activity(name="Еда")
    meat = Activity(name="Мясная продукция", parent=food)
    milk = Activity(name="Молочная продукция", parent=food)

    auto = Activity(name="Автомобили")
    trucks = Activity(name="Грузовые", parent=auto)
    cars = Activity(name="Легковые", parent=auto)
    parts = Activity(name="Запчасти", parent=cars)
    accessories = Activity(name="Аксессуары", parent=cars)

    session.add_all([food, meat, milk, auto, trucks, cars, parts, accessories])
    session.flush()

    b1 = Building(name='г. Москва, ул. Ленина 1', address="г. Москва, ул. Ленина 1", latitude=55.75, longitude=37.62)
    b2 = Building(name='г. Москва, ул. Блюхера 32/1', address="г. Москва, ул. Блюхера 32/1", latitude=55.751, longitude=37.621)
    session.add_all([b1, b2])
    session.flush()

    org1 = Organization(name="ООО Рога и Копыта", building_id=b2.id)
    session.add(org1)
    session.flush()

    session.add_all([
        Phone(number="2-222-222", organization_id=org1.id),
        Phone(number="3-333-333", organization_id=org1.id),
        Phone(number="8-923-666-13-13", organization_id=org1.id)
    ])

    org1.activities.extend([meat, milk])

    session.commit()

def downgrade():
    pass
