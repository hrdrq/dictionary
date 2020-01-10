# encoding: utf-8
import json
import unittest
from unittest.mock import Mock, patch, PropertyMock

import vcr

from test import DictTest
from server.ja.parser.naver import Naver
from server.forvo import Forvo

def pp(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

class TestParser(DictTest):

    def test_naver(self):
        with vcr.use_cassette('test/vcr_cassettes/naver_test.yaml'):
            res = Naver().search('テスト')
            self.assertEqual(res['status'], 'success')
            pp(res)

        with vcr.use_cassette('test/vcr_cassettes/naver_kino.yaml'):
            res = Naver().search('機能')
            self.assertEqual(res['status'], 'success')
            pp(res)

        with vcr.use_cassette('test/vcr_cassettes/naver_user.yaml'):
            res = Naver().search('ユーザー')
            self.assertEqual(res['status'], 'success')
            pp(res)

    @unittest.skip('')
    def test_forvo_en(self):
        with vcr.use_cassette('test/vcr_cassettes/forvo_en_test.yaml'):
            res = Forvo('en').search('test')
            self.assertEqual(res['status'], 'success')
            pp(res)

        with vcr.use_cassette('test/vcr_cassettes/forvo_en_fire.yaml'):
            res = Forvo('en').search('fire')
            self.assertEqual(res['status'], 'success')
            pp(res)

    def test_forvo_ja(self):
        with vcr.use_cassette('test/vcr_cassettes/forvo_ja_test.yaml'):
            res = Forvo('ja').search('テスト')
            self.assertEqual(res['status'], 'success')
            pp(res)

        with vcr.use_cassette('test/vcr_cassettes/forvo_ja_taihen.yaml'):
            res = Forvo('ja').search('大変')
            self.assertEqual(res['status'], 'success')
            pp(res)

        with vcr.use_cassette('test/vcr_cassettes/forvo_ja_nagai.yaml'):
            res = Forvo('ja').search('長い')
            self.assertEqual(res['status'], 'success')
            pp(res)

