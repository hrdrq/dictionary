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
        response = requests.get(self.URL.format(word=word), headers=headers)
        text = response.text

        # f = open('temp.txt')
        # text = f.read()
        # f.close()

        doc = PyQuery(text)
        results = []
        divs = doc('section div:has("section.entry-headword"):has(".pron-spell-container"):has(".pron-ipa-content")')
        if not divs:
            return []

        for def_div in divs:
            def_div = PyQuery(def_div)
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
                    label = meaning_div('.luna-label')
                    if label:
                        print('xxx', label.text())
                        x = label.text()
                        meaning_div('.luna-labset').replaceWith(x)
                        print(meaning_div)
                    text = meaning_div.children('span').clone().children().remove().end().text()
                    meaning = dict(text=text)
                    example = meaning_div('.luna-example').text()
                    if example:
                        meaning['example'] = example
                    sub_lis = meaning_div('li')
                    if sub_lis:
                        meaning['subs'] = list(map(lambda x: PyQuery(x).text(), sub_lis))

                    meanings.append(meaning)
                # print(len(meaning_divs))
                definitions.append(dict(
                    word_type=word_type,
                    meanings=meanings
                ))
            # print(len(definitions))
            # 定義
            results.append(dict(
                pron=pron,
                sound=sound,
                definitions=definitions
            ))
        return results

class Weblio(object):
    URL = "http://www.weblio.jp/content/{word}"

    def search(self, word):
        response = requests.get(self.URL.format(word=word), headers=headers)
        text = response.text
        # たまにhtmlに「𥝱」があって、処理はエラーが発生する
        text = text.replace('𥝱', '')

        doc = PyQuery(text)
        results = []
        normal_dict = doc("div.NetDicHead")
        if normal_dict:
            for head in normal_dict:
                result = {'word': word, 'type': 'normal'}
                head = PyQuery(head)
                # 括弧（【】）がある場合、漢字か外来語は入ってる
                match_kakko = re.compile(r"【(.*)】").search(head.text())
                if match_kakko:
                    kakko = match_kakko.group(1)
                    match_gairaigo = re.compile(r"[a-zA-Z]").search(kakko)
                    if match_gairaigo:
                        result['gogen'] = kakko
                        result['kana'] = word
                    else:
                        result['kanji'] = kakko
                        result['kana'] = head('b').text().replace(
                            ' ', '').replace('・', '')
                for accent in head('span'):
                    accent = PyQuery(accent)
                    match_accent = re.compile(
                        r"［([0-9]*)］").search(accent.text())
                    if match_accent:
                        result['accent'] = result.get(
                            'accent', '') + match_accent.group(1) + ','
                if 'accent' in result:
                    result['accent'] = result['accent'][:-1]
                body = head.next()
                for a in body('a'):
                    a = PyQuery(a)
                    a.replaceWith(a.html())
                result['meaning'] = body.html()
                # 単語自体は仮名のみの場合
                if 'kana' not in result:
                    result['kana'] = word
                results.append(result)

        Jitsu_dict = doc("div.Jtnhj")
        if Jitsu_dict:
            result = {'word': word, 'type': 'Jitsu'}
            match = re.compile(
                r"読み方：<!--\/AVOID_CROSSLINK-->(.*)<br/?><!--AVOID_CROSSLINK-->別表記").search(Jitsu_dict.html())
            if match:
                result['kana'] = match.group(1)
                if result['kana'].find('<a') != -1:
                    result['kana'] = PyQuery(result['kana']).text()
            else:
                match = re.compile(
                    r"読み方：<!--\/AVOID_CROSSLINK-->(.*)<br/?>").search(Jitsu_dict.html())
                if match:
                    result['kana'] = match.group(1)
                    if result['kana'].find('<a') != -1:
                        result['kana'] = PyQuery(result['kana']).text()

            if Jitsu_dict('.AM'):
                meaning = PyQuery('<div>')
                meaning.html(Jitsu_dict('.AM').nextAll())
            else:
                meaning = Jitsu_dict
            for a in meaning('a'):
                a = PyQuery(a)
                a.replaceWith(a.html())
            result['meaning'] = meaning.text()
            results.append(result)

        IT_dict = doc('div.Binit')
        if IT_dict:
            result = {'word': word, 'type': 'IT'}
            a = IT_dict('a').eq(0)
            if a.text().find('読み方') != -1:
                kana_tag = a.next('a').eq(0)
                result['kana'] = kana_tag.text().replace(' ', "")
            else:
                result['kana'] = word
                if IT_dict.text().find('【') != -1:
                    result['gogen'] = a.eq(0).text()
            for p in IT_dict('p'):
                p = PyQuery(p)
                for a in p('a'):
                    a = PyQuery(a)
                    a.replaceWith(a.html())
                if not p.html():
                    continue
                result['meaning'] = result.get(
                    'meaning', '') + "<p>" + p.html() + "</p>"
            result['kanji'] = IT_dict.prev("h2.midashigo").text()
            results.append(result)

        WIKI = doc('div.Wkpja')
        if WIKI:
            result = {'word': word, 'type': 'WIKI'}
            p = WIKI('p').not_(".WkpjaTs")
            for a in p('a'):
                a = PyQuery(a)
                a.replaceWith(a.html())
            result['meaning'] = p.html()
            result['kanji'] = WIKI.prev("h2.midashigo").text()
            results.append(result)
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
    print(json.dumps(d.search(a.word), indent=2, ensure_ascii=False))
