# encoding: utf-8
from __future__ import print_function, unicode_literals
import json
import decimal
import datetime
from io import BytesIO
import base64

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import boto3
from boto3.session import Session
from PIL import Image
from pydub import AudioSegment

from credentials import *


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        elif isinstance(o, unicode):
            return str(o)
        elif isinstance(o, datetime.datetime):
            return o.isoformat()

        return super(JSONEncoder, self).default(o)


def result_parse(data):
    '''
    テーブルインスタンスをJSONに変換
    '''
    data.detail
    result = data.__dict__
    result.pop('_sa_instance_state')
    detail = result.pop('detail').__dict__
    for key in ['id', '_sa_instance_state', 'created', 'updated']:
        del detail[key]
    for k, v in result.items():
        if type(v) == datetime.datetime:
            result[k] = v.strftime(format('%Y-%m-%d %H:%M:%S'))
        elif type(v) == datetime.date:
            result[k] = v.strftime(format('%Y-%m-%d'))
    result = {k: v for dic in [
        result, detail] for k, v in dic.items()}
    return result


def result_parse_ko(data):
    '''
    テーブルインスタンスをJSONに変換
    '''
    result = data.__dict__
    result.pop('_sa_instance_state')
    for k, v in result.items():
        if type(v) == datetime.datetime:
            result[k] = v.strftime(format('%Y-%m-%d %H:%M:%S'))
        elif type(v) == datetime.date:
            result[k] = v.strftime(format('%Y-%m-%d'))
    return result


def connect_db(host=None):
    if not host:
        host = DB_HOST
    ENGINE = create_engine('{dialect}+{driver}://{username}:{pwd}@{host}:{port}/{dbname}?charset=utf8'.format(
        dialect='mysql',
        driver='pymysql',
        username=DB_USERNAME,
        pwd=DB_PW,
        host=host,
        port=DB_PORT,
        dbname=DB_NAME
    ), echo=False)
    Session = sessionmaker(bind=ENGINE)
    # MySQLを処理するツール
    return Session()


def connect_s3():
    s3_session = Session(aws_access_key_id=ACCESS_KEY_ID,
                         aws_secret_access_key=SECRET_ACCESS_KEY,
                         region_name=REGION_NAME)

    return s3_session.resource('s3')

def base64_to_jpg(base64code):
    im = Image.open(BytesIO(base64.b64decode(base64code)))
    out = BytesIO()
    im.save(out, format='jpeg', quality=20)
    return out.getvalue()

def compress_mp3(data):
    sound = AudioSegment.from_file(BytesIO(data))
    out = BytesIO()
    sound.export(out, format="mp3", bitrate="32k")
    return out.getvalue()
