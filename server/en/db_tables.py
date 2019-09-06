# encoding: utf-8
# MySQLデータベースのスキーマを定義
# dict_jaテーブルとdict_ja_detailテーブルは一対多の関係

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Boolean, Column, create_engine, Integer, MetaData, String, Table, ForeignKey, text
)
from sqlalchemy.dialects.mysql import *
from sqlalchemy.orm import relation, relationship
Base = declarative_base()


class DictEN(Base):
    __tablename__ = 'dict_en'
    id = Column(INTEGER(11, unsigned=True),
                primary_key=True, autoincrement=True)
    created = Column(DATETIME, nullable=False,
                     server_default=text('CURRENT_TIMESTAMP'))
    updated = Column(DATETIME, nullable=False, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    word = Column(String)
    new = Column(BOOLEAN, default=None)
    has_updated = Column(BOOLEAN, default=None)
    type = Column(String, default=None)
    detail_id = Column(INTEGER(11, unsigned=True), ForeignKey(
        'dict_en_detail.id'), nullable=False, index=True)
    detail = relationship("DictENDetail")


class DictENDetail(Base):
    __tablename__ = 'dict_en_detail'
    id = Column(INTEGER(11, unsigned=True),
                primary_key=True, autoincrement=True)
    created = Column(DATETIME, nullable=False,
                     server_default=text('CURRENT_TIMESTAMP'))
    updated = Column(DATETIME, nullable=False, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    pron = Column(String, default=None)
    audio = Column(String, default=None)
    image = Column(String, default=None)
    meaning = Column(TEXT, default=None)
    example = Column(TEXT, default=None)
    forvo = Column(BOOLEAN, default=None)
