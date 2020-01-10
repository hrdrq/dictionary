# encoding: utf-8
import json
from unittest.mock import Mock, patch, PropertyMock

import vcr

from test import DictTest
from server.ja.parser import naver

class MockResponse:
    def __init__(self, file_name):
        with open(file_name) as f:
            self.json_data = json.load(f)

    def json(self):
        return self.json_data

def pp(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

class TestNaver(DictTest):
    # with patch('server.ja.parser.naver.requests.get') as mock:
    #     mock.return_value = MockResponse('test/naver_test.json')
    #     res = naver.Naver().search('apple')
    #     print(res)
    with vcr.use_cassette('test/vcr_cassettes/naver_test.yaml'):
        res = naver.Naver().search('テスト')
        pp(res)

    with vcr.use_cassette('test/vcr_cassettes/naver_kino.yaml'):
        res = naver.Naver().search('機能')
        pp(res)

    with vcr.use_cassette('test/vcr_cassettes/naver_user.yaml'):
        res = naver.Naver().search('ユーザー')
        pp(res)
