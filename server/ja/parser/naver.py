# encoding: utf-8
# Nサイトで音声を取得
# PyQueryでスクレイピング

import requests
import re
import lxml
from pyquery import PyQuery

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

class Naver(object):
    URL = 'https://ja.dict.naver.com/api3/jako/search?query="{word}"&m=mobile&range=word&page=1'

    def search(self, word):
        cleanr = re.compile('<.*?>')
        response = requests.get(self.URL.format(word=word), headers=headers)
        data = response.json()
        try:
            items = data['searchResultMap']['searchResultListMap']['WORD']['items']
        except:
            return {"status": 'error', "error_detail": "error getting 'items'"}
        try:
            results = []
            for item in items:
                if len(item['searchPhoneticSymbolList']) == 0:
                    continue
                res = {
                    'word': re.sub(cleanr, '', item['expKanji'] or item['handleEntry'])
                }
                url = item['searchPhoneticSymbolList'][0]['phoneticSymbolPath']
                match = re.compile(r"(http.*)\|").search(url)
                if match:
                    url = match.group(1)
                res['url'] = url
                results.append(res)
        except Exception as e:
            print(e)
            return {"status": 'error', "error_detail": "error parsing 'items'"}
        if results:
            return {"status": 'success', "results": results}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}

