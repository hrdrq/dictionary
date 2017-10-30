# encoding: utf-8
from __future__ import print_function, unicode_literals

import requests
import re

import mtranslate
from pyquery import PyQuery


class Naver(object):
    URL = 'http://krdic.naver.com/search.nhn?query={word}&kind=keyword'

    def search(self, word):
        print(self.URL.format(word=word))
        response = requests.get(self.URL.format(word=word))
        print(response.encoding)
        response.encoding = 'utf-8'
        doc = PyQuery(response.text)
        results = []
        # gs = goslate.Goslate()
        for li in doc("ul.lst3>li"):
            result = {}
            li = PyQuery(li)
            a = li('a.fnt15')
            if not a('strong'):
                continue
            li("sup").remove()
            li(".star").remove()
            pronounce = li('span.pronun')
            if pronounce:
                result['pronounce'] = pronounce.text().replace(
                    '[', '').replace(']', '')
                pronounce.remove()
            player_search = li(".player_search")
            if player_search:
                result['audio'] = player_search('.btn_play').attr('purl')
                player_search.remove()
            word = li('a.fnt15').text().split('(')
            result['word'] = word[0].replace(' ', '')
            if len(word) > 1:
                result['origin'] = word[1].replace(')', '')
            a.remove()
            li('button').remove()
            li('.syn').remove()
            result['meaning'] = li.text()
            try:
                result['translate'] = mtranslate.translate(
                    result['meaning'], "ja", "ko")
            except:
                import traceback
                traceback.print_exc()
            results.append(result)

        if results:
            return {"status": 'success', "results": results}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}
