# encoding: utf-8
# import concurrent.futures
import logging
import requests

import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.concurrent

from .search_handler import search_handler, suggest_handler
from .save_handler import save_handler
# from suggest_handler import suggest_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class JAHandler(tornado.web.RequestHandler):
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
        if path.find('/ja/search') != -1:
            res = search_handler(event)
            return(res)
        elif path.find('/ja/save') != -1:
            return(save_handler(event))
        elif path.find('/ja/suggest') != -1:
            return(suggest_handler(event))

    @tornado.gen.coroutine
    def get(self):
        result = yield self.get_()
        # print('xxxxx', result)
        self.write(result)

    def post(self):
        path = self.request.path
        event = {
            'queryParams': '',
            'path': path,
            'body': tornado.escape.json_decode(self.request.body),
            'method': 'POST'
        }
        if path.find('/ja/save') != -1:
            self.write(save_handler(event))

    def put(self):
        path = self.request.path
        event = {
            'queryParams': '',
            'path': path,
            'body': tornado.escape.json_decode(self.request.body),
            'method': 'PUT'
        }
        if path.find('/ja/update') != -1:
            self.write(save_handler(event))
