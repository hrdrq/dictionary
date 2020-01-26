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


class DictJA(Base):
    __tablename__ = 'dict_ja'
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
        'dict_ja_detail.id'), nullable=False, index=True)
    detail = relationship("DictJADetail")


class DictJADetail(Base):
    __tablename__ = 'dict_ja_detail'
    id = Column(INTEGER(11, unsigned=True),
                primary_key=True, autoincrement=True)
    created = Column(DATETIME, nullable=False,
                     server_default=text('CURRENT_TIMESTAMP'))
    updated = Column(DATETIME, nullable=False, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    kana = Column(String, default=None)
    gogen = Column(String, default=None)
    accent = Column(String, default=None)
    audio = Column(String, default=None)
    image = Column(String, default=None)
    meaning = Column(TEXT, nullable=False)
    example = Column(TEXT, default=None)
    examples = Column(TEXT, default=None)
    listening_hint = Column(TEXT, default=None)
    example_audio = Column(String, default=None)
    forvo = Column(BOOLEAN, default=None)
