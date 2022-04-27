import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, SerializerMixin):
    """Модель пользователя"""
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    chapter_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey('chapters.id'), default=0)
    event_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey('events.id'), default=0)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    chapter = orm.relation('Chapter')
    event = orm.relation('Event')

    def __repr__(self):
        return f'<User> {self.username}'
