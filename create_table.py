from sqlalchemy import MetaData, Table

from db import engine, sq


metadata_obj = MetaData()

Vkfinder = Table(
    'vkfinder', metadata_obj,
    sq.Column('id', sq.Integer, primary_key=True),
    sq.Column('user_id', sq.String(150), nullable=False),
    sq.Column('url', sq.String(150), nullable=False),
)

metadata_obj.create_all(engine)

print('таблицы созданы')
