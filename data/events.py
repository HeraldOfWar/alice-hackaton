import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Event(SqlAlchemyBase, SerializerMixin):
    """Модель события"""
    __tablename__ = 'events'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    chapter_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey('chapters.id'))
    next_events = sqlalchemy.Column(sqlalchemy.PickleType, nullable=True)
    buttons = sqlalchemy.Column(sqlalchemy.PickleType, nullable=True)
    chapter = orm.relation('Chapter')
    users = orm.relation('User', back_populates='event')

    def __repr__(self):
        return f'<Event> {self.id}'
