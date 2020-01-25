# encoding: utf-8
import json
import os
from datetime import datetime
import unittest
from unittest.mock import Mock, patch, PropertyMock

import vcr

from test import DictTest
from test.image_base64 import CODE
from server.en.save_handler import Save

def pp(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

BODY = {
    "word": "apple",
    "pron": "ˈæp əl",
    "meaning": '<div class="meaning"><div class="definition"><div class="word_type">noun</div><div class="meanings"><div class="meaning_list"><div class="text">the usually round, red or yellow, edible fruit of a small tree, Malus sylvestris, of the rose family</div></div><div class="meaning_list"><div class="text">the tree, cultivated in most temperate regions</div></div><div class="meaning_list"><div class="text">the fruit of any of certain other species of tree of the same genus</div></div><div class="meaning_list"><div class="text">any of these trees</div></div><div class="meaning_list"><div class="text">any of various other similar fruits, or fruitlike products or plants, as the custard apple, love apple, May apple, or oak apple</div></div><div class="meaning_list"><div class="text">anything resembling an apple in size and shape, as a ball, especially a baseball</div></div><div class="meaning_list"><div class="text">Bowling. an ineffectively bowled ball</div></div><div class="meaning_list"><div class="text">Slang. a red capsule containing a barbiturate, especially secobarbital</div></div></div></div></div>',
    "audio": "https://static.sfdict.com/audio/A06/A0612000.mp3",
    "example": "Is that apple pie I smell?",
    "image": CODE,
    "type": "normal"
}

class MockDictEN:
    def __init__(self, **data):
        return 

class MockDictENDetail:
    def __init__(self, **data):
        return 

class MockS3():
    pass

class MockSql():

    def close(self):
        pass

    def add(self, data):
        pass

    def commit(self):
        pass

    def refresh(self, data):
        pass

def mock_connect_db():
    return MockSql()

def mock_connect_s3():
    return MockS3()

now_str = datetime.now().strftime("%m%d%H%M%S")
dir_str = 'test/res/'
os.makedirs(dir_str + 'image', exist_ok=True)
def mock_save_to_s3(self, name, data):
    if name.startswith('image'):
        file_name = dir_str + 'image/' + now_str +name[6:]
    else:
        file_name = dir_str + now_str + name
    with open(file_name, 'wb') as f:
        f.write(data)

def mock_result_parse(data):
    return data

class TestSave(DictTest):

    @patch('server.en.save_handler.DictEN', MockDictEN)
    @patch('server.en.save_handler.DictENDetail', MockDictENDetail)
    @patch('server.en.save_handler.result_parse', mock_result_parse)
    @patch('server.en.save_handler.connect_db', mock_connect_db)
    @patch('server.en.save_handler.connect_s3', mock_connect_s3)
    @patch('server.en.save_handler.Save.save_to_s3', mock_save_to_s3)
    def test_en_save_file(self):
        with vcr.use_cassette('test/vcr_cassettes/en_save.yaml'):
            Save().save(BODY)

