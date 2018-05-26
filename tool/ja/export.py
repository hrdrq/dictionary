# encoding: utf-8
from __future__ import print_function, unicode_literals
import sys
sys.path.append('../../server')
sys.path.append('../../server/ja')


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
# DB_HOST = '13.112.211.132'
from db_tables import DictJA, DictJADetail
from utils import result_parse, connect_db, connect_s3, JSONEncoder

FIELDS = ['word', 'kana', 'gogen', 'accent', 'meaning', 'chinese', 'example', 'listening_hint','examples', 'image', 'audio']

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
        res = self.sql.query(DictJA)\
            .filter(DictJA.new == True)\
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
                os.system('for f in *.mp3; do sox $f o/$f reverse silence 1 0.01 0.5% reverse silence 1 0.01 0.5%; done')
                os.system('mp3gain -r o/*.mp3')
                os.system('mp3gain -r forvo/*.mp3')
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
                'dict-ja', file_name, local_file_name)
        except Exception as e:
            print("例外args:", e.args)

    # def s3_download_dir(self, dist, root_dist, local='/tmp', bucket='dict-ja'):
    #     paginator = self.s3.meta.client.get_paginator('list_objects')
    #     for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=dist):
    #         if result.get('CommonPrefixes') is not None:
    #             for subdir in result.get('CommonPrefixes'):
    #                 self.s3_download_dir(subdir.get(
    #                     'Prefix'), root_dist, local, bucket)
    #         if result.get('Contents') is not None:
    #             for file in result.get('Contents'):
    #                 if file.get('Key').endswith('/'):
    #                     continue

    #                 local_file_name = local + os.sep + \
    #                     file.get('Key').replace(root_dist, '')
    #                 if not os.path.exists(os.path.dirname(local_file_name)):
    #                     os.makedirs(os.path.dirname(local_file_name))
    #                 self.s3.meta.client.download_file(
    #                     bucket, file.get('Key'), local_file_name)

    # def s3_move_files(self, dist, root_dist, bucket='dict-ja'):
    #     paginator = self.s3.meta.client.get_paginator('list_objects')
    #     for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=dist):
    #         if result.get('CommonPrefixes') is not None:
    #             for subdir in result.get('CommonPrefixes'):
    #                 self.s3_move_files(subdir.get(
    #                     'Prefix'), root_dist, bucket)
    #         if result.get('Contents') is not None:
    #             for file in result.get('Contents'):
    #                 if file.get('Key').endswith('/'):
    #                     continue
    #                 print(file.get('Key'))
    #                 self.s3.Object(bucket, file.get('Key').replace(root_dist, '')).copy_from(
    #                     CopySource=bucket + '/' + file.get('Key'))

    # def s3_export(self):
    #     media_folder = './{}/media'.format(self.today)
    #     # self.s3_download_dir('new/', 'new/', media_folder)
    #     self.s3_move_files('new/', 'new/', '/')


if __name__ == '__main__':
    argvs = sys.argv
    if(len(argvs) > 1 and argvs[1] == 'update_db'):
        update_db = True
    print("update_db: {}".format(update_db))
    # sys.exit()
    export = Export()
    # export.s3_move_files('new/', '/')
    export.export()
    # print(json.dumps(export.s3_export(), indent=4,
    #                  ensure_ascii=False, cls=JSONEncoder))
    # print(datetime.datetime.now().strftime('%Y%m%d'))
