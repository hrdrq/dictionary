# encoding: utf-8
# 日本語辞書のメインファイル

import logging
import requests

import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.concurrent

from .search_handler import search_handler
from .save_handler import save_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# @tornado.concurrent.run_on_executorと
# @tornado.gen.coroutineは
# requestsの処理を並行させるために追加
class ENHandler(tornado.web.RequestHandler):
    # 非同期処理があるので追加した
    # thread poolは５くらいがあれば大丈夫だと思う
    executor = tornado.concurrent.futures.ThreadPoolExecutor(5)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET,PUT,POST,OPTIONS")
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, X-Requested-By,If-Modified-Since, X-File-Name, Cache-Control")

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    @tornado.concurrent.run_on_executor
    def get_(self):
        # queryParams = {k: v[0] for k, v in self.request.arguments.items()}
        path = self.request.path
        event = {
            'queryParams': {k: v[0] for k, v in self.request.arguments.items()},
            'path': path,
            'body': '',
            'method': 'GET'
        }
        if path.find('/en/search') != -1:
            return search_handler(event)
        elif path.find('/en/save') != -1:
            return save_handler(event)
        elif path.find('/en/suggest') != -1:
            return suggest_handler(event)

    @tornado.gen.coroutine
    def get(self):
        result = yield self.get_()
        self.write(result)

    @tornado.concurrent.run_on_executor
    def post_(self):
        path = self.request.path
        event = {
            'queryParams': '',
            'path': path,
            'body': tornado.escape.json_decode(self.request.body),
            'method': 'POST'
        }
        if path.find('/en/save') != -1:
            return save_handler(event)


    @tornado.gen.coroutine
    def post(self):
        result = yield self.post_()
        self.write(result)

    @tornado.concurrent.run_on_executor
    def put_(self):
        path = self.request.path
        event = {
            'queryParams': '',
            'path': path,
            'body': tornado.escape.json_decode(self.request.body),
            'method': 'PUT'
        }
        if path.find('/en/update') != -1:
            return save_handler(event)

    @tornado.gen.coroutine
    def put(self):
        result = yield self.put_()
        self.write(result)
