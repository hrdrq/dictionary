# encoding: utf-8

import requests
import re
from pyquery import PyQuery


class Kpedia(object):
    URL = "http://www.kpedia.jp/s/2/{word}"

    def search(self, word):
        response = requests.get(self.URL.format(word=word))
        text = response.text

        doc = PyQuery(text)
        results = []
        table = doc("table.school-course")
        if table:
            # print(table)
            # table = table[0]
            table = PyQuery(table)
            for tr in table('tr'):
                tr = PyQuery(tr)
                if tr('th'):
                    continue

                td = tr('td')
                td = PyQuery(td)

                result = {'word': td.eq(0).text().split('（')[0], 'meaning': td.eq(
                    1).text()}
                if result['word'][-1] == ' ':
                    result['word'] = result['word'][:-1]
                results.append(result)
        if results:
            return {"status": 'success', "results": results}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}
