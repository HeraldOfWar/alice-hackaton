import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Chapter(SqlAlchemyBase, SerializerMixin):
    """Модель главы"""
    __tablename__ = 'chapters'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    users = orm.relation('User', back_populates='chapter')
    events = orm.relation('Event', back_populates='chapter')

    def __repr__(self):
        return f'<Chapter> {self.title}'
