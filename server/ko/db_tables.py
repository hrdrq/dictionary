# encoding: utf-8
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Boolean, Column, create_engine, Integer, MetaData, String, Table, ForeignKey, text
)
from sqlalchemy.dialects.mysql import *
Base = declarative_base()


class DictKO(Base):
    __tablename__ = 'dict_ko'
    id = Column(INTEGER(11, unsigned=True),
                primary_key=True, autoincrement=True)
    created = Column(DATETIME, nullable=False,
                     server_default=text('CURRENT_TIMESTAMP'))
    updated = Column(DATETIME, nullable=False, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    word = Column(String)
    new = Column(BOOLEAN, default=None)
    pronounce = Column(String, default=None)
    origin = Column(String, default=None)
    audio = Column(String, nullable=False)
    image = Column(String, nullable=False)
    meaning = Column(TEXT, nullable=False)
    japanese = Column(TEXT, nullable=False)
    chinese = Column(TEXT, nullable=False)
