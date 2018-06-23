# encoding: utf-8
# Nサイトで音声を取得
# PyQueryでスクレイピング

import requests
import re
import lxml
from pyquery import PyQuery

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}


class Naver(object):
    URL = 'http://jpdic.naver.com/search.nhn?range=word&q="{word}"'

    def search(self, word):
        response = requests.get(self.URL.format(word=word), headers=headers)
        doc = PyQuery(response.text)
        results = []
        for item in doc("div.srch_top"):
            result = {}
            item = PyQuery(item)
            url = item('span.player')('button.play').attr('data-purl')
            if url:
                match = re.compile(r"(http.*)\|").search(url)
                if match:
                    url = match.group(1)
                result['url'] = url
                for s in item('span.jp'):
                    s = PyQuery(s)
                    result['word'] = result.get('word', '') + s.text()
                results.append(result)

        if results:
            return {"status": 'success', "results": results}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}
