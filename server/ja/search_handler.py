# encoding: utf-8
# 検索処理（日本語、中国語、音声、例文、画像）
# 各パーサーを分岐し、classを定義
# 例：
# /ja/search/query?word=テスト
# /ja/search/meaning?word=テスト
# /ja/search/audio/naver?word=テスト

# クライアントは最初にqueryして、同じ単語がなかったら、
# 他の検索を全部投げる

import logging
from sqlalchemy import create_engine, func, or_, and_
from sqlalchemy.orm import sessionmaker, aliased

from .parser.weblio import Weblio
from .parser.hujiang import Hujiang
from .parser.naver import Naver
from .parser.yourei import Yourei
from .parser.forvo import Forvo
from .db_tables import DictJA
from .image_search import image_search

import sys
sys.path.append('../../')
from utils import result_parse, connect_db


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# データベースにクエリし、同じ単語がある場合、「duplicated」を返す
class Query(object):

    def __init__(self):
        self.sql = connect_db()

    def search(self, word):
        res = self.sql.query(DictJA)\
            .filter(DictJA.word == word)\
            .first()
        if res:
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


def search_handler(event):
    params = event['queryParams']
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
