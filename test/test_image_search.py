# encoding: utf-8
import json
import unittest
from unittest.mock import Mock, patch, PropertyMock

import vcr

from test import DictTest
from server.image_search import image_search 

class TestImageSearch(DictTest):

    def test_asyncio(self):
        image_search('nickel', lang='en')
