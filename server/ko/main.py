# encoding: utf-8

import logging
import requests

import tornado.ioloop
import tornado.web

from .search_handler import search_handler, suggest_handler
from .save_handler import save_handler
# from suggest_handler import suggest_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class KOHandler(tornado.web.RequestHandler):

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
        # queryParams = {k: v[0] for k, v in self.request.arguments.items()}
        path = self.request.path
        event = {
            'queryParams': {k: v[0] for k, v in self.request.arguments.items()},
            'path': path,
            'body': '',
            'method': 'GET'
        }
        if path.find('/ko/search') != -1:
            self.write(search_handler(event))
        elif path.find('/ko/save') != -1:
            self.write(save_handler(event))
        elif path.find('/ko/suggest') != -1:
            self.write(suggest_handler(event))

    def post(self):
        path = self.request.path
        print(self.request.body)
        event = {
            'queryParams': '',
            'path': path,
            'body': tornado.escape.json_decode(self.request.body),
            'method': 'POST'
        }
        if path.find('/ko/save') != -1:
            self.write(save_handler(event))

    def put(self):
        path = self.request.path
        event = {
            'queryParams': '',
            'path': path,
            'body': tornado.escape.json_decode(self.request.body),
            'method': 'PUT'
        }
        if path.find('/ko/update') != -1:
            self.write(save_handler(event))
