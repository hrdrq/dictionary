# encoding: utf-8
# 更新された単語のバージョン
# TODO：export.pyに統合

from __future__ import print_function, unicode_literals
import sys
sys.path.append('../../server')
sys.path.append('../../server/ja')


import os
import json
import csv
import re
import datetime
import boto3
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import aliased

from credentials import *
from db_tables import DictJA, DictJADetail
from utils import result_parse, connect_db, connect_s3, JSONEncoder

FIELDS = ['word', 'kana', 'gogen', 'accent', 'meaning', 'example', 'listening_hint','examples', 'image']
FIELDS_COLLECT = ['word', 'kana', 'gogen', 'accent', 'meaning', 'image']

update_db = False


class Export(object):

    def __init__(self):
        self.sql = connect_db(DB_HOST)
        self.s3 = connect_s3()
        self.today = datetime.datetime.now().strftime('%Y%m%d') + '_'
        self.writer_normal = None
        self.writer_IT = None
        self.writer_name = None
        self.writer_collect = None

    def __del__(self):
        self.sql.close()


    def write_collect(self, row_dict):
        if not self.writer_collect:
            if not os.path.exists("./{}".format(self.today)):
                os.makedirs("./{}".format(self.today))
            f = open('./{}/collect.csv'.format(self.today), 'w')
            self.writer_collect = csv.DictWriter(
                f, fieldnames=FIELDS_COLLECT, lineterminator='\n')
        self.writer_collect.writerow(row_dict)

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
        res = self.sql.query(DictJA)\
            .filter(DictJA.has_updated == True)\
            .all()
        if res:
            if update_db:
                for r in res:
                    r.has_updated = False
                self.sql.commit()
            else:
                for r in res:
                    if r.new:
                        continue
                    print(r.id,r.word)
                    data = result_parse(r)
                    write_data = {}
                    type = data.get('type')
                    if type == 'collect':
                        for key in FIELDS_COLLECT:
                            value = data.get(key, '') or ''
                            if key == 'image':
                                if value != '':
                                    for i in value.split(','):
                                        write_data[key] = write_data.get(
                                            key, '') + '<img src="{}" />'.format(i)
                                        self.s3_download_file('image/' + i)
                                else:
                                    write_data[key] = ''
                            else:
                                write_data[key] = value
                        self.write_collect(write_data)
                    else:
                        for key in FIELDS:
                            value = data.get(key, '') or ''
                            if key == 'image':
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
