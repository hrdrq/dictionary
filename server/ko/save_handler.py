# encoding: utf-8

import logging
import requests
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import aliased
import base64
import uuid
import jaconv

from .db_tables import DictKO
from credentials import *
from server.utils import result_parse_ko, connect_db, connect_s3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Save(object):

    def __init__(self):
        self.sql = connect_db()
        self.s3 = connect_s3()

    def save(self, data):
        if 'audio' in data:
            audio = data['audio']
            if type(audio) == list:
                name_list = []
                for a in audio:
                    response = requests.get(a['url'])
                    audio_data = response.content
                    audio_name = a['file_name'] + '.mp3'
                    self.s3.Object(KO_BUCKET_NAME, audio_name).put(
                        Body=audio_data)
                    name_list.append(audio_name)
                data['audio'] = ','.join(name_list)
            else:
                response = requests.get(audio)
                audio_data = response.content
                audio_name = data['word'] + '.mp3'
                self.s3.Object(KO_BUCKET_NAME, audio_name).put(Body=audio_data)
                data['audio'] = audio_name
        if 'image' in data:
            image_name = str(uuid.uuid4()) + '.png'
            self.s3.Object(KO_BUCKET_NAME, 'image/' + image_name).put(
                Body=base64.b64decode(data['image']))
            data['image'] = image_name
        if 'kana' in data:
            data['kana'] = jaconv.kata2hira(
                data['kana']).replace(' ', '').replace('　', '')
        # data_ = {'word': data.pop('word')}
        data['new'] = True
        print(data)
        dict_ko = DictKO(**data)
        # sessionに追加
        self.sql.add(dict_ko)
        # sessionデータをMySQLに更新する
        self.sql.commit()
        # データベースと一致させる
        self.sql.refresh(dict_ko)
        result = result_parse_ko(dict_ko)
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

    if path == '/ko/save':
        if method != 'POST':
            return {'status': 'error', 'error_detail': 'Only POST is supported.'}

        res = save.save(data)
    else:
        return {'status': 'error', 'error_detail': 'The Path is not supported.'}

    return res
