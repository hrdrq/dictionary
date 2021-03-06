# encoding: utf-8
# データベースに入ってる新しく追加された単語をcsv、音声、画像の形にエクスポートする
# mp3gainを使い、音量を統一
# soxを使い、ファイルの前後の無音の部分をtrimする
# （mp3gainとsoxは事前にインストールする必要がある）
# 使い方：
# python export.py           →エクスポート
# python export.py update_db →「新しい単語」というフラグをリセット

from __future__ import print_function, unicode_literals
import sys
sys.path.append('../..')
sys.path.append('../../server')
sys.path.append('../../server/en')


import os
import json
import csv
import re
import datetime
import traceback
import boto3
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import aliased

from credentials import *
from db_tables import DictEN, DictENDetail
from utils import result_parse, connect_db, connect_s3, JSONEncoder

FIELDS = ['word', 'pron', 'meaning', 'example', 'image', 'audio']

update_db = False


class Export(object):

    def __init__(self):
        self.sql = connect_db(DB_HOST)
        self.s3 = connect_s3()
        self.today = datetime.datetime.now().strftime('%Y%m%d')
        self.writer_normal = None
        self.writer_IT = None
        self.writer_name = None

    def __del__(self):
        self.sql.close()

    def write_normal(self, row_dict):
        if not self.writer_normal:
            if not os.path.exists("./{}".format(self.today)):
                os.makedirs("./{}".format(self.today))
            f = open('./{}/normal.csv'.format(self.today), 'w')
            self.writer_normal = csv.DictWriter(
                f, fieldnames=FIELDS, lineterminator='\n')
        self.writer_normal.writerow(row_dict)

    def write_IT(self, row_dict):
        if not self.writer_IT:
            if not os.path.exists("./{}".format(self.today)):
                os.makedirs("./{}".format(self.today))
            f = open('./{}/IT.csv'.format(self.today), 'w')
            self.writer_IT = csv.DictWriter(
                f, fieldnames=FIELDS, lineterminator='\n')
        self.writer_IT.writerow(row_dict)

    def write_name(self, row_dict):
        if not self.writer_name:
            if not os.path.exists("./{}".format(self.today)):
                os.makedirs("./{}".format(self.today))
            f = open('./{}/name.csv'.format(self.today), 'w')
            self.writer_name = csv.DictWriter(
                f, fieldnames=FIELDS, lineterminator='\n')
        self.writer_name.writerow(row_dict)

    def export(self):
        res = self.sql.query(DictEN)\
            .filter(DictEN.new == True)\
            .all()
        if res:
            if update_db:
                for r in res:
                    r.new = False
                    r.has_updated = False
                self.sql.commit()
            else:
                for r in res:
                    print(r.id,r.word)
                    data = result_parse(r)
                    write_data = {}
                    type = data.get('type')
                    for key in FIELDS:
                        value = data.get(key, '') or ''
                        if key == 'audio':
                            if value != '':
                                for a in value.split(','):
                                    write_data[key] = write_data.get(
                                        key, '') + '[sound:{}]'.format(a)
                                    self.s3_download_file(a, data.get('forvo'))
                            else:
                                write_data[key] = '[sound:{}.mp3]'.format(data[
                                                                          'word'])
                        elif key == 'image':
                            if value != '':
                                for i in value.split(','):
                                    write_data[key] = write_data.get(
                                        key, '') + '<img src="{}" />'.format(i)
                                    self.s3_download_file('image/' + i)
                            else:
                                write_data[key] = ''
                        else:
                            write_data[key] = value
                    if type == 'normal':
                        self.write_normal(write_data)
                    elif type == 'IT':
                        self.write_IT(write_data)
                    elif type == 'name':
                        self.write_name(write_data)
                folder = "./{}/media/".format(self.today)
                os.chdir(folder)
                os.mkdir('o')
                os.system('for f in *.mp3; do sox $f o/$f reverse silence 1 0.01 -55d reverse silence 1 0.01 -55d; done')
                os.system('mp3gain -r o/*.mp3')
        else:
            print('新しい単語がない')

    def s3_download_file(self, file_name, forvo=False):
        folder = "./{}/media/".format(self.today)
        local_file_name = folder + ("forvo/" if forvo else "") + file_name
        print(local_file_name)
        if not os.path.exists(os.path.dirname(local_file_name)):
            os.makedirs(os.path.dirname(local_file_name))
        try:
            self.s3.meta.client.download_file(
                BUCKET_NAME, file_name, local_file_name)
        except Exception as e:
            print("例外args:", e.args)


if __name__ == '__main__':
    argvs = sys.argv
    if(len(argvs) > 1 and argvs[1] == 'update_db'):
        update_db = True
    print("update_db: {}".format(update_db))
    export = Export()
    export.export()
