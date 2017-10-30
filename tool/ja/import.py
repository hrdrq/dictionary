# encoding: utf-8
from __future__ import print_function, unicode_literals
import json
import csv
import re

from save_handler import save_handler
from search_handler import search_handler
from json_encoder import JSONEncoder

COL1 = [
    'word',
    'meaning',
    'chinese',
    'kana',
    'gogen',
    'accent',
    'audio_list',
    'image_list',
    'need_update',
]


def import1():
    f = open('collect.csv', 'r')

    reader = csv.reader(f)
    # header = next(reader)
    for row in reader:
        req = {'type': 'collect'}
        for idx, val in enumerate(row):
            if idx == 8:
                tags = val.decode('utf-8').split(' ')
                if 'word' not in tags:
                    req[COL1[idx]] = True
            elif val != '':
                req[COL1[idx]] = val.decode('utf-8')
                if idx == 1 or idx == 2:
                    req[COL1[idx]] = re.sub(ur'\"{2}', "$", req[COL1[idx]]).replace('"', '').replace('$', '"')
                    # print(req[COL[idx]])
                if idx == 6:
                    match = re.findall(ur'\[sound:(.*?)\]', req[COL1[idx]])
                    req[COL1[idx]] = [m for m in match]
                if idx == 7:
                    match = re.findall(ur'src=""(.*?)""', req[COL1[idx]])
                    req[COL1[idx]] = [m for m in match]
        post_data = {
            'method': 'POST',
            'headers': {
                'content-type': 'application/json',
            },
            'path': '/ja/save',
            'queryParams': {
            },
            'body': req
        }
        print(req['word'])
        res = save_handler(post_data)
        # print(json.dumps(res, indent=4, ensure_ascii=False, cls=JSONEncoder))

    f.close()

COL2 = [
    'word',
    'meaning',
    'chinese',
    'audio_list',
    'kana',
    'gogen',
    'accent',
    'image_list',
    'addReverse',
    'type',
]


def import2():
    f = open('collect3.csv', 'r')

    reader = csv.reader(f)
    # header = next(reader)
    for row in reader:
        req = {}
        for idx, val in enumerate(row):
            if val != '':
                req[COL2[idx]] = val.decode('utf-8')
                if idx == 1 or idx == 2:
                    req[COL2[idx]] = re.sub(ur'\"{2}', "$", req[COL2[idx]]).replace('"', '').replace('$', '"')
                    # print(req[COL[idx]])
                if idx == 3:
                    match = re.findall(ur'\[sound:(.*?)\]', req[COL2[idx]])
                    req[COL2[idx]] = [m for m in match]
                if idx == 7:
                    match = re.findall(ur'src=""(.*?)""', req[COL2[idx]])
                    req[COL2[idx]] = [m for m in match]
        post_data = {
            'method': 'POST',
            'headers': {
                'content-type': 'application/json',
            },
            'path': '/ja/save',
            'queryParams': {
            },
            'body': req
        }
        print(req['word'])
        res = save_handler(post_data)
        # print(json.dumps(req, indent=4, ensure_ascii=False, cls=JSONEncoder))

    f.close()

if __name__ == '__main__':
    import2()
