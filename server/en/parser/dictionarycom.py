# encoding: utf-8

import requests
import re
from pyquery import PyQuery
import pdb
debug = pdb.set_trace

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}

class Dictionarycom(object):
    URL = "https://www.dictionary.com/browse/{word}"

    def search(self, word):
        # print(self.URL.format(word=word))
        response = requests.get(self.URL.format(word=word.replace(' ', '-')), headers=headers)
        text = response.text

        # f = open('temp.txt')
        # text = f.read()
        # f.close()

        doc = PyQuery(text)
        results = []
        if ' ' in word:
            divs = doc('section div:has("section.entry-headword")')
        else:
            divs = doc('section div:has("section.entry-headword"):has(".pron-spell-container"):has(".pron-ipa-content")')
        if not divs:
            return {"status": 'error', "error_detail": "Nothing found."}

        for def_div in divs:
            def_div = PyQuery(def_div)
            # 単語
            word = def_div('h1,h2').text()
            # 単語

            # 発音
            pron = def_div('.pron-ipa-content').text()
            if pron == '':
                pron = None
            else:
                pron = pron.replace(' ', '').replace('/', '')
            # 発音

            # 音声
            sound = def_div('audio source[type="audio/mpeg"]').attr('src')
            # 音声

            # 定義
            definitions = []
            meaning_section = def_div('section:not(.entry-headword)')

            for section in meaning_section:
                # debug()
                section = PyQuery(section)
                word_type = section('h3').text()
                meanings = []
                meaning_divs = section('.default-content>div, .expandable-content>div')
                if not meaning_divs:
                    meaning_divs = section.children('div>div')
                for meaning_div in meaning_divs:
                    meaning_div = PyQuery(meaning_div)
                    # label = meaning_div('.luna-label')
                    # if label:
                    #     # print('xxx', label.text())
                    #     x = label.text()
                    #     meaning_div('.luna-labset').replaceWith(x)
                    #     # print(meaning_div)
                    # a = meaning_div('a')
                    # if a:
                    #     x = a.text()
                    #     meaning_div('a').replaceWith(x)
                    # decoration = meaning_div('.italic, .bold')
                    # if decoration:
                    #     # debug()
                    #     for _decoration in decoration:
                    #
                    #         # x = decoration.text()
                    #         _decoration.replaceWith(_decoration.text())
                    # text = meaning_div.children('span').clone().children().remove().end().text()

                    meaning = dict()
                    example = meaning_div('.luna-example').text()
                    if example:
                        meaning['example'] = example
                    sub_lis = meaning_div('li')
                    if sub_lis:
                        meaning['subs'] = list(map(lambda x: PyQuery(x).text(), sub_lis))

                    meaning_div('.luna-example').remove()
                    meaning_div('li').remove()
                    text = meaning_div.text()[:-1]
                    meaning['text'] = text

                    meanings.append(meaning)
                # print(len(meaning_divs))
                definitions.append(dict(
                    word_type=word_type,
                    meanings=meanings
                ))
            # print(len(definitions))
            # 定義
            results.append(dict(
                word=word,
                pron=pron,
                sound=sound,
                definitions=definitions
            ))
        if results:
            return {"status": 'success', "results": results}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}

if __name__ == '__main__':
    import json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--word', default='test')
    a = parser.parse_args()
    d = Dictionarycom()
    print('word:', a.word)
    print(json.dumps(d.search(a.word), indent=2, ensure_ascii=False))
