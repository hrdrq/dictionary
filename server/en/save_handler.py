# encoding: utf-8

import logging
import requests
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import aliased
import base64
import uuid

from .db_tables import DictEN, DictENDetail
from credentials import *
from utils import result_parse, connect_db, connect_s3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.WARNING)


class Save(object):

    def __init__(self):
        self.sql = connect_db()
        self.s3 = connect_s3()

    def __del__(self):
        self.sql.close()

    def save_to_s3(self, name, data):
        # return
        self.s3.Object(BUCKET_NAME, name).put(Body=data)

    def save(self, data):
        if 'audio' in data:
            audio = data['audio']
            if type(audio) == list:
                name_list = []
                for a in audio:
                    if a['url'].find('forvo') > -1:
                        data['forvo'] = True
                    response = requests.get(a['url'])
                    audio_data = response.content
                    audio_name = a['file_name'].replace(' ', '_') + '.mp3'
                    self.save_to_s3(audio_name, audio_data)
                    name_list.append(audio_name)
                data['audio'] = ','.join(name_list)
            else:
                audio_name = data['word'].replace(' ', '_') + '.mp3'
                if audio:
                    if audio.find('forvo') > -1:
                        data['forvo'] = True
                    response = requests.get(audio)
                    audio_data = response.content
                    self.save_to_s3(audio_name, audio_data)
                data['audio'] = audio_name
        if 'image' in data:
            image_name = str(uuid.uuid4()) + '.png'
            self.save_to_s3('image/' + image_name, base64.b64decode(data['image']))
            data['image'] = image_name
        data_ = {'word': data.pop('word')}
        data_['new'] = True

        for key in ['need_update', 'type', 'addReverse']:
            if key in data:
                data_[key] = data.pop(key)

        # テーブルinstance作成
        dict_en_detail = DictENDetail(**data)
        data_['detail'] = dict_en_detail
        dict_en = DictEN(**data_)
        # sessionに追加
        self.sql.add(dict_en)
        # sessionデータをMySQLに更新する
        self.sql.commit()
        # データベースと一致させる
        self.sql.refresh(dict_en)
        result = result_parse(dict_en)
        return {
            "status": 'success',
            "result": result
        }

    def update(self, data):
        id = data.pop('id')
        raw = self.sql.query(DictEN)\
            .filter(DictEN.id == id)\
            .first()
        if 'image' in data:
            image_name = str(uuid.uuid4()) + '.png'
            self.save_to_s3('image/' + image_name, base64.b64decode(data['image']))
            data['image'] = image_name
        for key in data:
            setattr(raw.detail, key, data[key])
        raw.has_updated = True

        # sessionデータをMySQLに更新する
        self.sql.commit()
        # データベースと一致させる
        self.sql.refresh(raw)
        result = result_parse(raw)
        return {
            "status": 'success',
            "result": result
        }



def save_handler(event):
    data = event['body']
    params = event['queryParams']
    method = event['method']
    path = event['path']

    save = Save()

    if path == '/en/save':
        if method != 'POST':
            return {'status': 'error', 'error_detail': 'Only POST is supported.'}

        res = save.save(data)
    elif path == '/en/update':
        res = save.update(data)
    else:
        return {'status': 'error', 'error_detail': 'The Path is not supported.'}

    return res
