# encoding: utf-8

import logging
from sqlalchemy import create_engine, func, or_, and_
from sqlalchemy.orm import sessionmaker, aliased

from .parser.kpedia import Kpedia
from .parser.hujiang import Hujiang
from .parser.naver import Naver
from .parser.forvo import Forvo
from .db_tables import DictKO
# import tables
import sys
sys.path.append('../../')
from utils import result_parse_ko, connect_db


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Query(object):

    def __init__(self):
        self.sql = connect_db()

    def search(self, word):
        res = self.sql.query(DictKO)\
            .filter(DictKO.word == word)\
            .first()
        if res:
            return {
                'status': 'duplicated',
                'result': result_parse_ko(res)
            }
        else:
            return {
                'status': 'success',
            }


def search_handler(event):
    params = event['queryParams']
    # method = event['method']
    path = event['path']
    print("path", path)
    if path == '/ko/search/query':
        search = Query()
    elif path == '/ko/search/meaning':
        search = Naver()
    elif path == '/ko/search/japanese':
        search = Kpedia()
    elif path == '/ko/search/chinese':
        search = Hujiang()
    # elif path == '/ko/search/audio/naver':
    #     search = Naver()
    elif path == '/ko/search/audio/forvo':
        search = Forvo()
    elif path == '/ko/search/audio/forvo/add':
        forvo = Forvo()
        return forvo.add(params['word'].decode('utf-8'))

    if params.get('word'):
        return search.search(params['word'].decode('utf-8'))
    else:
        return {'error': True, 'message': 'The param "word" is needed.'}


import requests
URL = 'https://dictionary.goo.ne.jp/suggest/all/{word}/{limit}/'


class Suggest(object):

    def search(self, word, limit=10):
        headers = {
            'Cookie': 'NGUserID=x; DICTUID=x',
        }
        res = requests.get(URL.format(word=word, limit=limit),
                           headers=headers).text

        # print(res.encode('utf-8'))
        # res = res.encode('utf-8')
        # print(type(res))
        # print(res.encoding)
        res = res.split('\t')
        count = int(res[0])
        if count > 0:
            return {"status": 'success', "results": res[2:]}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}
        # print(res)
        # return res
        # return {"status": 'success', "results": results}


def suggest_handler(event):
    params = event['queryParams']
    # method = event['method']
    path = event['path']

    if params.get('word'):
        suggest = Suggest()
        return suggest.search(params['word'].decode('utf-8'), limit=params.get('limit', 10))
    else:
        return {'error': True, 'message': 'The param "word" is needed.'}
