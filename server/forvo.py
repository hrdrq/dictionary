# encoding: utf-8
# Fサイトで音声を取得と、単語発音を依頼
# PyQueryでスクレイピング
# word：単語
# user：発音したユーザのID
# word_id：単語のID（既存する単語を別のユーザに発音してもらう時に使う）

import logging
import re
import json
import js2py
from pyquery import PyQuery
import requests
import asyncio
import time
import pdb
debug = pdb.set_trace

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

# 最初はsearchを読んで、各ページのURLを取得し、
# 並行処理で各ページの情報を取得
# addメソッド：新しい単語として、発音を依頼する
# requestメソッド：既存する単語を別のユーザに発音してもらう
class Forvo(object):

    def __init__(self, lang='ja'):
        self.results = []
        self.lang = lang
        if lang == 'ja':
            self.id_lang = "76"
        elif lang == 'en':
            self.id_lang = "39"
        self.URL = 'https://ja.forvo.com/search/{word}/%s/' % lang

    def base64_decode(self, code):
        return js2py.eval_js(JS)(code)

    @staticmethod
    async def do_request(urls):
        def requests_get_wrapper(url):
            try:
                return requests.get(url)
            except :
                return None
        results = []
        loop = asyncio.get_event_loop()
        for url in urls:
            req = loop.run_in_executor(None, requests_get_wrapper, url)
            res = await req
            if res:
                results.append(res.text)
        return results

    def parse_items(self, urls):
        loop = asyncio.get_event_loop()
        docs = loop.run_until_complete(self.do_request(urls))
        for item_response_body in docs:
            word_id = None
            match = re.search("notSatisfied(Lang)?\( ?'(\d+)' ?[,\)]", item_response_body)
            if match:
                word_id = match.group(2)
            item_doc = PyQuery(item_response_body)
            for locale in item_doc("article.pronunciations"):
                locale = PyQuery(locale)
                lang_header = locale('header[id=%s] em' % self.lang)
                # debug()
                if lang_header:
                    word = re.compile(
                        r"(.*) の発音").search(lang_header.text()).group(1)
                    for i in locale('span.play'):
                        i = PyQuery(i)
                        text = i.parents('li').eq(0).text()
                        user = None
                        match = re.search("発音したユーザ: (.*) \(", text)
                        if match:
                            user = match.group(1)
                        onclick = i.attr('onclick')
                        match = re.compile(
                            r"Play\(.*,'(.*)',.*,.*,.*,.*,.*\)").search(onclick)
                        if match:
                            code = match.group(1)
                            url = 'https://audio00.forvo.com/mp3/' + \
                                self.base64_decode(code)
                            self.results.append({'word': word, 'url': url, 'word_id': word_id, 'user': user})

    def search(self, word):
        response = requests.get(self.URL.format(word=word), headers=headers)
        doc = PyQuery(response.text)
        page_urls = ['https://ja.forvo.com' +
                     PyQuery(x).attr('href') for x in doc('nav.pagination')('a.num')]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        if page_urls:
            loop = asyncio.get_event_loop()
            docs = loop.run_until_complete(self.do_request(page_urls))
            docs.append(doc)
        else:
            docs = [doc]
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