# encoding: utf-8

import logging
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

URL = 'http://dictionary.goo.ne.jp/suggest/all/{word}/{limit}/'


class Suggest(object):

    def search(self, word, limit=10):
        headers = {
            'Cookie': 'NGUserID=x; DICTUID=x',
        }
        res = requests.post(URL.format(word=word, limit=limit),
                            headers=headers).text

        # print(res.encode('utf-8'))
        # res = res.encode('utf-8')
        # print(type(res))
        res = res.split('\t')
        count = int(res[0])
        if count > 0:
            return {"status": 'success', "results": res[2:]}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}
        # print(res)
        # return res
        # return {"status": 'success', "results": results}


def suggest_handle(event):
    params = event['queryParams']
    # method = event['method']
    path = event['path']

    if params.get('word'):
        suggest = Suggest()
        return suggest.search(params['word'], limit=params.get('limit', 5))
    else:
        return {'error': True, 'message': 'The param "word" is needed.'}
