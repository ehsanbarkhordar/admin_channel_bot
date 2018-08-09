from datetime import datetime

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, String, MetaData, Integer, Float, Boolean, Text, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.dialects.postgresql import insert

from bot_config import BotConfig
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


#
# class Admin(Base):
#     __tablename__ = 'admin'
#     id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
#     name = Column(String, nullable=False)
#     user_id = Column(Integer, nullable=False, unique=True)
#     access_hash = Column(String, nullable=False)
#     is_super_admin = Column(Boolean, default=False)
#
#     def __init__(self, name, user_id, access_hash):
#         self.name = name
#         self.user_id = user_id
#         self.access_hash = access_hash
#
#     def __repr__(self):
#         return "<User(name='%s',user_id='%i',access_hash='%s',is_super_admin='%s')>" % (
#             self.name, self.user_id, self.access_hash, self.is_super_admin)


class Content(Base):
    __tablename__ = 'content'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    channel_name = Column(String, nullable=False)
    channel_description = Column(Text, nullable=False)
    channel_nick_name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    channel_logo_id = Column(Integer, ForeignKey('logo.id'), nullable=False)
    create_date = Column(DateTime, default=datetime.now())
    is_publish = Column(Integer, default=0, nullable=False)
    publish_date = Column(DateTime)
    user_id = Column(Integer, nullable=False)
    access_hash = Column(String, nullable=False)

    def __init__(self, channel_name, channel_description, channel_nick_name, category_id, channel_logo_id, user_id,
                 access_hash):
        self.channel_name = channel_name
        self.channel_description = channel_description
        self.channel_nick_name = channel_nick_name
        self.category_id = category_id
        self.channel_logo_id = channel_logo_id
        self.user_id = user_id
        self.access_hash = access_hash

    def __repr__(self):
        return "<Content(channel_name='%s',channel_description='%s',channel_nick_name='%s'" \
               ",category_id='%s',channel_logo_id='%s',user_id='%i',access_hash='%s')>" % (
                   self.channel_name, self.channel_description, self.channel_nick_name, self.category_id,
                   self.channel_logo_id, self.user_id, self.access_hash)


#
# class Channel(Base):
#     __tablename__ = 'channel'
#     id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
#     name = Column(String, nullable=False)
#     channel_id = Column(Integer, nullable=False)
#     channel_access_hash = Column(String, nullable=False)
#     content = relationship("Content")
#
#     def __init__(self, name, channel_id, channel_access_hash, content):
#         self.name = name
#         self.channel_id = channel_id
#         self.channel_access_hash = channel_access_hash
#         self.content = content


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    content = relationship("Content")

    def __init__(self, name):
        self.name = name


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
        content.is_publish = status_code
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


def change_description(content_id, description):
    content = session.query(Content).filter(Content.id == content_id).one_or_none()
    try:
        content.channel_description = description
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


def get_unpublished_content():
    return session.query(Content).filter(Content.is_publish != 1).order_by(Content.create_date).limit(
        BotConfig.rows_per_query).all()


def get_accept_content():
    return session.query(Content).filter(Content.is_publish == 1).order_by(Content.create_date).all()


# def insert_channel(channel):
#     try:
#         session.add(channel)
#         session.commit()
#         return True
#     except ValueError:
#         print(ValueError)
#         return False


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
    try:
        session.add(category)
        session.commit()
        return True
    except ValueError:
        print(ValueError)
        return False


#
# def get_all_channels():
#     return session.query(Channel).all()
#

# def get_channel_by_name(channel_name):
#     return session.query(Channel).filter(Channel.name == channel_name).one_or_none()
#


def get_all_categories():
    return session.query(Category).all()


def get_category_by_name(category_name):
    return session.query(Category).filter(Category.name == category_name).one_or_none()


def get_category_by_id(category_id):
    return session.query(Category).filter(Category.id == category_id).one_or_none()


def get_logo_by_fileid_access_hash(file_id, access_hash):
    return session.query(Logo).filter(Logo.file_id == file_id, Logo.access_hash == access_hash).one_or_none()


def get_logo_by_id(logo_id):
    return session.query(Logo).filter(Logo.id == logo_id).one_or_none()


def get_content_by_id(content_id):
    return session.query(Content).filter(Content.id == content_id).one_or_none()

# def insert_user(name, user_id, access_hash):
#     insert_stmt = insert(User).values(user_id=user_id, access_hash=access_hash)
#     on_update_stmt = insert_stmt.on_conflict_do_update(
#         index_elements=['user_id'],
#         set_=dict(final_oauth_token=final_oauth_token,
#                   final_oauth_token_secret=final_oauth_token_secret))
#     try:
#         result = db.execute(on_update_stmt)
#         session.commit()
#         return result
#     except ValueError:
#         print(ValueError)
#         return False
#
#
# def get_user(user_id):
#     return session.query(User).filter(User.user_id == user_id).one_or_none()
