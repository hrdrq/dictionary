# encoding: utf-8

import logging
import requests
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import aliased
import base64
import uuid
import jaconv
import csv
import re

from db_tables import DictJA, DictJADetail
import sys
sys.path.append('../')
from credentials import *
from utils import result_parse, connect_db, connect_s3
# from .rhinospike import add_sentence_one_time

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
                    self.s3.Object(BUCKET_NAME, audio_name).put(
                        Body=audio_data)
                    name_list.append(audio_name)
                data['audio'] = ','.join(name_list)
            else:
                response = requests.get(audio)
                audio_data = response.content
                audio_name = data['word'] + '.mp3'
                self.s3.Object(BUCKET_NAME, audio_name).put(Body=audio_data)
                data['audio'] = audio_name
        if 'image' in data:
            image_name = str(uuid.uuid4()) + '.png'
            self.s3.Object(BUCKET_NAME, 'image/' + image_name).put(
                Body=base64.b64decode(data['image']))
            data['image'] = image_name
        # import用
        if 'audio_list' in data:
            data['audio'] = ','.join(data.pop('audio_list'))
        # import用
        if 'image_list' in data:
            data['image'] = ','.join(data.pop('image_list'))
        if 'kana' in data:
            data['kana'] = jaconv.kata2hira(
                data['kana']).replace(' ', '').replace('　', '')
        data_ = {'word': data.pop('word')}
        # import用
        for key in ['need_update', 'type', 'addReverse']:
            if key in data:
                data_[key] = data.pop(key)
        data_['new'] = True

        if data.get('example'):
            if not add_sentence_one_time(data['example']):
                data['need_add_example_audio'] = True

        # テーブルinstance作成
        dict_ja_detail = DictJADetail(**data)
        data_['detail'] = dict_ja_detail
        dict_ja = DictJA(**data_)
        # sessionに追加
        self.sql.add(dict_ja)
        # sessionデータをMySQLに更新する
        self.sql.commit()
        # データベースと一致させる
        self.sql.refresh(dict_ja)
        result = result_parse(dict_ja)
        return {
            "status": 'success',
            "result": result
        }

    def update(self, data):
        id = data.pop('id')
        raw = self.sql.query(DictJA)\
            .filter(DictJA.id == id)\
            .first()
        if 'kana' in data:
            data['kana'] = jaconv.kata2hira(
                data['kana']).replace(' ', '').replace('　', '')
        for key in data:
            setattr(raw.detail, key, data[key])
        raw.has_updated = True
        # raw.new = True

        # sessionデータをMySQLに更新する
        self.sql.commit()
        # データベースと一致させる
        self.sql.refresh(raw)
        result = result_parse(raw)
        return {
            "status": 'success',
            "result": result
        }

    def query(self, kana):
        res = self.sql.query(DictJA)\
            .filter(DictJA.detail.has(DictJADetail.kana == jaconv.kata2hira(kana)))\
            .all()
        if res:
            return {
                'status': 'duplicated',
                'results': [result_parse(r) for r in res]
            }
        else:
            return {
                'status': 'success',
            }

    def add_alternative_word(self, data):
        res = self.sql.query(DictJA)\
            .filter(DictJA.word == data['word'])\
            .first()
        if res:
            return {
                "status": 'error',
                "error_detail": 'もう追加された'
            }
        dict_ja = DictJA(**data)
        # sessionに追加
        self.sql.add(dict_ja)
        # sessionデータをMySQLに更新する
        self.sql.commit()
        # データベースと一致させる
        self.sql.refresh(dict_ja)
        result = result_parse(dict_ja)
        return {
            "status": 'success',
            "result": result
        }


if __name__ == '__main__':
    sql = connect_db()
    f = open('jj2.csv', 'r')
    ff = open('ee2.csv', 'w')
    writer = csv.writer(ff, lineterminator='\n')
    reader = csv.reader(f)
    for row in reader:
        word = row[0]
        sentence = row[1]
        # sound = row[2]

        listening_hint = re.sub(r'\[.+?\]', '', sentence)
        listening_hint = listening_hint.replace(' ', '')
        listening_hint = re.sub(r'<b>.+?</b>', '＿', listening_hint)
        listening_hint = re.sub(r'＿+', '＿', listening_hint)

        # iterator = re.finditer(r'\[sound:(.+?)\]', sound)
        # sound = ','.join([match.group(1) for match in iterator])
        print(word, listening_hint)

        writer.writerow([word, listening_hint])

        # dict_ja = sql.query(DictJA)\
        #     .filter(DictJA.word == word)\
        #     .first()
        # dict_ja.detail.example = sentence
        # dict_ja.detail.listening_hint = listening_hint
        # dict_ja.detail.example_audio = sound
        # sql.commit()
