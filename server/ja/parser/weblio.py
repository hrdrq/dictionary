# encoding: utf-8

import requests
import re
from pyquery import PyQuery

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}


class Weblio(object):
    URL = "http://www.weblio.jp/content/{word}"

    def search(self, word):
        response = requests.get(self.URL.format(word=word), headers=headers)
        # print(response.text)
        text = response.text
        text = text.replace('𥝱', '')

        doc = PyQuery(text)
        results = []
        normal_dict = doc("div.NetDicHead")
        if normal_dict:
            for head in normal_dict:
                result = {'word': word, 'type': 'normal'}
                head = PyQuery(head)
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
                if 'kana' not in result:
                    result['kana'] = word
                results.append(result)
        # else:
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
            # print(Jitsu_dict('.AM'))
            # meaning.html(Jitsu_dict('.AM').nextAll())
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
