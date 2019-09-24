# encoding: utf-8

import requests
import re
from pyquery import PyQuery
import pdb
debug = pdb.set_trace

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}

class Yourdictionary(object):
    URL = "https://api.yourdictionary.com/words/{word}/sentences/en?limit=250"

    def search(self, word):
        response = requests.get(self.URL.format(word=word), headers=headers).json()
        if ('Code' in response and response['Code'] == 'NotFoundError') or ('message' in response and 'No results found for word' in response['message']):
            return {"status": 'error', "error_detail": "Nothing found."}
        else:
            return {"status": 'success', "results": response['data']['sentences']}

if __name__ == '__main__':
    import json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--word', default='test')
    a = parser.parse_args()
    d = Yourdictionary()
    print(json.dumps(d.search(a.word), indent=2, ensure_ascii=False))
