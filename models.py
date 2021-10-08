from sqlalchemy.orm import declarative_base
import sqlalchemy as sq


Base = declarative_base()


class Vkfinder(Base):

    __tablename__ = 'vkfinder'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.String(150), nullable=False)
    url = sq.Column(sq.String(150), nullable=False)
