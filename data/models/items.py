import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.models.db_session import SqlAlchemyBase


class Item(SqlAlchemyBase, SerializerMixin):
    """Модель вещи"""
    __tablename__ = 'items'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)

    def __repr__(self):
        return f'<Item> {self.title}'
