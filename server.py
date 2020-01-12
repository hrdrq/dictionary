# encoding: utf-8
# サーバのルートファイル。
# サーバはtornadoを使ってる
# データベースはMySQLを使い、ライブラリはsqlalchemyを使ってる
# URLのパスを判断し、使うハンドラーを分岐する
# 機密情報はcredentials.pyに書いてある。gitにコミットしない

from __future__ import print_function, unicode_literals
import os
import pdb
d = pdb.set_trace

import requests
import tornado.ioloop
import tornado.web
import urllib.parse

# 日本語辞書
from server.ja.main import JAHandler
# 韓国語辞書（メンテナンスしてない）
from server.ko.main import KOHandler
from server.en.main import ENHandler

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
# CORSのないサイトのファイルをダウンロードするためのプロクシ
def proxy(event):
    url = event['queryParams'].get('url')
    if not url:
        return
    r = requests.get(url, headers=headers)
    return {
        'Content-Type': r.headers['Content-Type'],
        'data': r.content
    }

# 今はプロクシの場合だけ
class MainHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET,PUT,POST,OPTIONS")
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, X-Requested-By,If-Modified-Since, X-File-Name, Cache-Control")

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    def get(self):
        path = self.request.path
        print('path', path)
        event = {
            'queryParams': {k: v[0] for k, v in self.request.arguments.items()},
            'path': path,
            'body': '',
            'method': 'GET'
        }
        if path.find('/proxy') != -1:
            res = proxy(event)
            self.set_header("Content-Type", res['Content-Type'])
            # d()
            filename = event['queryParams'].get('filename').decode()
            self.set_header("Content-Disposition", "attachment;filename={};".format(urllib.parse.quote(filename)))
            self.write(res['data'])
        else:
            self.write({
                "results": 'success',
            })

settings = {"debug": True}
application = tornado.web.Application([
    (r"/ja/.*", JAHandler),
    (r"/ko/.*", KOHandler),
    (r"/en/.*", ENHandler),
    (r"/.*", MainHandler)
], static_path=os.path.join(os.getcwd(),  "static"), **settings)

if __name__ == "__main__":
    application.listen(8889)
    tornado.ioloop.IOLoop.instance().start()
