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

from .parser.dictionarycom import Dictionarycom
from .parser.yourdictionary import Yourdictionary
from .db_tables import DictEN

from server.utils import result_parse, connect_db
from server.forvo import Forvo
from server.image_search import image_search


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# データベースにクエリし、同じ単語がある場合、「duplicated」を返す
class Query(object):

    def __init__(self):
        self.sql = connect_db()

    def search(self, word):
        res = self.sql.query(DictEN)\
            .filter(DictEN.word == word)\
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
    if path == '/en/search/query':
        search = Query()
    elif path == '/en/search/meaning':
        search = Dictionarycom()
    elif path == '/en/search/audio/forvo':
        search = Forvo('en')
    elif path == '/en/search/audio/forvo/add':
        forvo = Forvo('en')
        return forvo.add(params['word'].decode('utf-8'))
    elif path == '/en/search/audio/forvo/request':
        forvo = Forvo('en')
        return forvo.request(params['word_id'].decode('utf-8'))
    elif path == '/en/search/example':
        search = Yourdictionary()
    elif path == '/en/search/image':
        return image_search(params['word'].decode('utf-8'), lang='en')

    if params.get('word'):
        return search.search(params['word'].decode('utf-8'))
    else:
        return {'error': True, 'message': 'The param "word" is needed.'}
