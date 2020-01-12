# encoding: utf-8
# Fサイトで音声を取得と、単語発音を依頼
# PyQueryでスクレイピング
# word：単語
# user：発音したユーザのID
# word_id：単語のID（既存する単語を別のユーザに発音してもらう時に使う）

import logging
import threading
import re
import json
import js2py
from pyquery import PyQuery
import requests
import asyncio
import time
import pdb
d = pdb.set_trace

# import sys
# sys.path.append('../../../')
from credentials import FORVO_USER, FORVO_PW

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# FサイトにあったJavaScriptソースコード。
# 音声ファイルのURLをdecrypt用
JS = '''function base64_decode(a) {
    var b, c, d, e, f, g, h, i, j = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
        k = ac = 0,
        l = "",
        m = [];
    if (!a) return a;
    a += "";
    do e = j.indexOf(a.charAt(k++)), f = j.indexOf(a.charAt(k++)), g = j.indexOf(a.charAt(k++)), h = j.indexOf(a.charAt(k++)), i = e << 18 | f << 12 | g << 6 | h, b = i >> 16 & 255, c = i >> 8 & 255, d = 255 & i, 64 == g ? m[ac++] = String.fromCharCode(b) : 64 == h ? m[ac++] = String.fromCharCode(b, c) : m[ac++] = String.fromCharCode(b, c, d); while (k < a.length);
    l = m.join("");
    xa = l;
    var xb = [],
        xc = 0,
        xd = 0,
        xe = 0,
        xf = 0,
        xg = 0;
    for (xa += ""; xc < xa.length;) xe = xa.charCodeAt(xc), 128 > xe ? (xb[xd++] = String.fromCharCode(xe), xc++) : xe > 191 && 224 > xe ? (xf = xa.charCodeAt(xc + 1), xb[xd++] = String.fromCharCode((31 & xe) << 6 | 63 & xf), xc += 2) : (xf = xa.charCodeAt(xc + 1), xg = xa.charCodeAt(xc + 2), xb[xd++] = String.fromCharCode((15 & xe) << 12 | (63 & xf) << 6 | 63 & xg), xc += 3);
    l = xb.join("")
    return l
}'''

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}

def base64_decode(code):
    return js2py.eval_js(JS)(code)

def get(url, res):
    try:
        response = requests.get(url, headers=headers)
        res.append(PyQuery(response.text))
    except:
        res.append(None)

# 最初はsearchを読んで、各ページのURLを取得し、
# 並行処理で各ページの情報を取得
# addメソッド：新しい単語として、発音を依頼する
# requestメソッド：既存する単語を別のユーザに発音してもらう
class Forvo(object):

    def __init__(self, lang='ja'):
        self.results = []
        if lang == 'ja':
            self.id_lang = "76"
        elif lang == 'en':
            lang = 'en_usa'
            self.id_lang = "39"
        self.URL = 'https://ja.forvo.com/search/{word}/%s/' % lang
        self.lang = lang

    def parse_items(self, urls):
        docs = []
        threads = [threading.Thread(target=get, args=(url, docs)) for url in urls]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        for item_doc in docs:
            word_id = None
            match = re.search("notSatisfied(Lang)?\( ?'(\d+)' ?[,\)]", item_doc.html())
            if match:
                word_id = match.group(2)
            for locale in item_doc("article.pronunciations"):
                locale = PyQuery(locale)
                lang_header = locale('header[id=%s]' % self.lang.split('_')[0])
                if lang_header:
                    word = re.compile(
                        r"(.*) の発音").search(lang_header.text()).group(1)
                    if self.lang == 'en_usa':
                        els = locale('header[id=%s]' % self.lang).next_all()
                    else:
                        els = locale('.show-all-pronunciations li')
                    lis = []
                    for el in els:
                      el = PyQuery(el)
                      if el.has_class('li-ad'):
                        continue
                      if el.is_('header'):
                        break
                      lis.append(el)
                    for li in lis:
                        i = PyQuery(li('span.play'))
                        text = i.parents('li').eq(0).text()
                        user = None
                        match = re.search("発音したユーザ: (.*) \(", text)
                        if match:
                            user = match.group(1)
                        onclick = i.attr('onclick')
                        match = re.compile(r"Play\(.*,'(.*)',.*,.*,.*,.*,.*\)").search(onclick)
                        if match:
                            code = match.group(1)
                            url = 'https://audio00.forvo.com/mp3/' + \
                                base64_decode(code)
                            self.results.append({'word': word, 'url': url, 'word_id': word_id, 'user': user})
                        else:
                            match = re.compile(r"PlayPhrase\(.*,'(.*)',.*\)").search(onclick)
                            if match:
                                code = match.group(1)
                                url = 'https://audio00.forvo.com/phrases/mp3/' + \
                                    base64_decode(code)
                                self.results.append({'word': word, 'url': url, 'word_id': word_id, 'user': user})

    def search(self, word):
        response = requests.get(self.URL.format(word=word), headers=headers)
        doc = PyQuery(response.text)
        page_urls = [PyQuery(x).attr('href') for x in doc('nav.pagination')('a.num')]
        docs = [doc]
        if page_urls:
            threads = [threading.Thread(target=get, args=(url, docs)) for url in page_urls]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        urls = []
        if self.lang == 'en_usa':
            found = False
            for doc in docs:
                if found:
                    break
                for href in doc("article.search_words li.list-words a.word, article.search_words li.list-phrases a.word"):
                    href = PyQuery(href)
                    # print(href.text().upper())
                    if href.text().upper() == word.upper():
                        urls = [href.attr('href')]
                        found = True
                        break
        else:
            urls = [PyQuery(x).attr('href') for doc in docs for x in doc(
                "article.search_words")("li.list-words")("a.word")]
        self.parse_items(urls)

        if self.results:
            return {"status": 'success', "results": self.results}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}

    def add(self, word):
        url = "https://ja.forvo.com/word-add/"

        # ログイン処理
        s = requests.Session()
        s.post('https://ja.forvo.com/login/',
               data={'login': FORVO_USER, 'password': FORVO_PW}, headers=headers)

        # 依頼処理
        # res = s.get(url)
        # if res.status_code == 200:
        #     return {"status": 'success'}
        # else:
        #     return {"status": 'error', "error_detail": res.status_code}
        res = s.post(url, data={
            "word": word,
            "id_lang": self.id_lang,
            "tags": "",
            "current_tags": "",
            "modify": "0",
            "is_phrase": "0"
        })
        return {"status": 'success'}

    def request(self, word_id):
        url = "https://ja.forvo.com/notsatisfied/"

        # ログイン処理
        s = requests.Session()
        s.post('https://ja.forvo.com/login/',
               data={'login': FORVO_USER, 'password': FORVO_PW}, headers=headers)

        # 依頼処理
        # res = s.get(url)
        # if res.status_code == 200:
        #     return {"status": 'success'}
        # else:
        #     return {"status": 'error', "error_detail": res.status_code}
        res = s.post(url, data={
            "f": "requestPronounciation",
            "idLang": self.id_lang,
            "idWord": str(word_id)
        })
        return {"status": 'success'}

if __name__ == '__main__':
    import json
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--word', default='test')
    parser.add_argument('-l', '--lang', default='en')
    a = parser.parse_args()
    d = Forvo(lang=a.lang)
    print(json.dumps(d.search(a.word), indent=2, ensure_ascii=False))
