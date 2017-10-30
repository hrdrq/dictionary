# encoding: utf-8

import logging
from sqlalchemy import create_engine, func, or_, and_
from sqlalchemy.orm import sessionmaker, aliased

from .parser.weblio import Weblio
from .parser.hujiang import Hujiang
from .parser.naver import Naver
from .parser.yourei import Yourei
from .parser.forvo import Forvo
from .db_tables import DictJA, Example
from .image_search import image_search
# import tables
import sys
sys.path.append('../../')
from utils import result_parse, connect_db


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Query(object):

    def __init__(self):
        self.sql = connect_db()

    def search(self, word):
        res = self.sql.query(DictJA)\
            .filter(DictJA.word == word)\
            .first()
        if res:
            print(res.need_update)
            if res.need_update:
                return {
                    'status': 'need_update',
                    'result': result_parse(res)
                }
            else:
                return {
                    'status': 'duplicated',
                    'result': result_parse(res)
                }
        else:
            return {
                'status': 'success',
            }

    def __del__(self):
        self.sql.close()


def search_example_from_db(word):
    sql = connect_db()
    res = sql.query(Example)\
        .filter(Example.word.has(word=word)).all()
    if res:
        results = [{
            "sentence_plain": r.sentence_plain,
            "listening_hint": r.listening_hint,
            "sentence": r.sentence
        } for r in res]
        return {"status": 'success', "results": results}
    else:
        return {"status": 'error', "error_detail": "Nothing found."}


def search_handler(event):
    params = event['queryParams']
    # method = event['method']
    path = event['path']
    print("path", path)
    if path == '/ja/search/query':
        search = Query()
    elif path == '/ja/search/meaning':
        search = Weblio()
    elif path == '/ja/search/chinese':
        search = Hujiang()
    elif path == '/ja/search/audio/naver':
        search = Naver()
    elif path == '/ja/search/audio/forvo':
        search = Forvo()
    elif path == '/ja/search/audio/forvo/add':
        forvo = Forvo()
        return forvo.add(params['word'].decode('utf-8'))
    elif path == '/ja/search/audio/forvo/request':
        forvo = Forvo()
        return forvo.request(params['word_id'].decode('utf-8'))
    elif path == '/ja/search/example':
        # naver = Naver()
        # return naver.example(params['word'].decode('utf-8'))
        yourei = Yourei()
        res = yourei.search(params['word'].decode(
            'utf-8'), 20, int(params.get('offset', 1)))
        if res['status'] == 'success':
            res['type'] = 'yourei'
            return res
        else:
            naver = Naver()
            return naver.example(params['word'].decode('utf-8'))
    elif path == '/ja/search/example_db':
        return search_example_from_db(params['word'].decode('utf-8'))
    elif path == '/ja/search/image':
        return image_search(params['word'].decode('utf-8'))

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
