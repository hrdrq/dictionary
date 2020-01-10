# -*- coding: utf-8 -*-

import unittest

main = unittest.main

class DictTest(unittest.TestCase):

    @property
    def debug(self):
        import pdb
        return pdb.set_trace
