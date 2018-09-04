from datetime import datetime

from sqlalchemy import create_engine, ForeignKey, or_, PrimaryKeyConstraint, Table
from sqlalchemy import Column, String, MetaData, Integer, Float, Boolean, Text, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

from bot_config import BotConfig
from constant.message import ReadyMessage
from db.db_config import DatabaseConfig
from balebot.utils.logger import Logger

my_logger = Logger.get_logger()

db_string = DatabaseConfig.db_string
db = create_engine(db_string)
meta = MetaData(db)
Base = declarative_base()
Session = sessionmaker(db)
session = Session()


def create_all_table():
    Base.metadata.create_all(db)
    return True


class Type(Base):
    __tablename__ = 'type'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    category = relationship("Category")

    def __init__(self, name):
        self.name = name


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    type_id = Column(Integer, ForeignKey('type.id'))

    def __init__(self, name, type_id):
        self.name = name
        self.type_id = type_id


# class ContentToCategory(Base):
#     __tablename__ = 'content_to_category'
#     content_id = Column(Integer, ForeignKey('content.id'), primary_key=True)
#     category_id = Column(Integer, ForeignKey('category.id'), primary_key=True)
#
#     def __init__(self, content_id, category_id):
#         self.content_id = content_id
#         self.category_id = category_id
ContentToCategory = Table('content_to_category', Base.metadata,
                          Column('content_id', Integer, ForeignKey('content.id')),
                          Column('category_id', Integer, ForeignKey('category.id'))
                          )


class Content(Base):
    __tablename__ = 'content'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    nick_name = Column(String, nullable=False)
    category = relationship("Category", secondary=ContentToCategory, backref="content")
    logo_id = Column(Integer, ForeignKey('logo.id'), nullable=False)
    create_date = Column(DateTime, default=datetime.now())
    allow_publish = Column(Integer, default=0, nullable=False)
    is_sent = Column(Integer, default=0, nullable=False)
    publish_date = Column(DateTime)
    user_id = Column(Integer, nullable=False)
    access_hash = Column(String, nullable=False)

    def __init__(self, name, description, nick_name, type_id, logo_id, user_id, access_hash):
        self.name = name
        self.description = description
        self.nick_name = nick_name
        self.type_id = type_id
        self.logo_id = logo_id
        self.user_id = user_id
        self.access_hash = access_hash

    def __repr__(self):
        return "<Content(name='%s',description='%s',nick_name='%s'" \
               ",category='%s',type_id='%s',logo_id='%s',user_id='%i',access_hash='%s')>" % (
                   self.name, self.description, self.nick_name, self.category, self.type_id,
                   self.logo_id, self.user_id, self.access_hash)


class Logo(Base):
    __tablename__ = 'logo'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    file_id = Column(BigInteger, nullable=False)
    access_hash = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    thumb = Column(String)
    content = relationship("Content")

    def __init__(self, file_id, access_hash, file_size, thumb):
        self.file_id = file_id
        self.access_hash = access_hash
        self.file_size = file_size
        self.thumb = thumb


def change_publish_status(content_id, status_code):
    content = session.query(Content).filter(Content.id == content_id).one_or_none()
    try:
        content.allow_publish = status_code
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


def change_description(content_id, description):
    content = session.query(Content).filter(Content.id == content_id).one_or_none()
    try:
        content.description = description
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


def change_logo(content_id, logo_id):
    content = session.query(Content).filter(Content.id == content_id).one_or_none()
    try:
        content.logo_id = logo_id
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


def change_is_sent(content_id, is_sent):
    content = session.query(Content).filter(Content.id == content_id).one_or_none()
    try:
        content.is_sent = int(is_sent)
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


def get_unpublished_content():
    return session.query(Content).filter(Content.is_sent == 0).filter(
        or_(Content.allow_publish == 0, Content.allow_publish == 2)).order_by(
        Content.create_date).limit(BotConfig.rows_per_query).all()


def get_accept_content():
    return session.query(Content).filter(Content.is_sent == 0).filter(Content.allow_publish == 1).order_by(
        Content.create_date).all()


def insert_content(content):
    try:
        session.add(content)
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


def insert_logo(logo):
    try:
        session.add(logo)
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


def insert_category(category):
    category_old = session.query(Category).filter(Category.name == category.name).one_or_none()
    if category_old:
        return ReadyMessage.duplicated_category
    try:
        session.add(category)
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


def insert_type(new_type):
    type_old = session.query(Type).filter(Type.name == new_type.name).one_or_none()
    if type_old:
        return ReadyMessage.duplicated_type
    try:
        session.add(new_type)
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


def get_all_categories():
    return session.query(Category).all()


def get_all_type():
    return session.query(Type).all()


def get_category_by_name(category_name):
    return session.query(Category).filter(Category.name == category_name).one_or_none()


def get_type_by_name(type_name):
    return session.query(Type).filter(Type.name == type_name).one_or_none()


def get_category_by_id(category_id):
    return session.query(Category).filter(Category.id == category_id).one_or_none()


def get_logo_by_fileid_access_hash(file_id, access_hash):
    return session.query(Logo).filter(Logo.file_id == file_id, Logo.access_hash == access_hash).one_or_none()


def get_logo_by_id(logo_id):
    return session.query(Logo).filter(Logo.id == logo_id).one_or_none()


def get_content_by_id(content_id):
    return session.query(Content).filter(Content.id == content_id).one_or_none()
