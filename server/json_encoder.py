# encoding: utf-8
from __future__ import print_function, unicode_literals

import time
import json
import decimal
import datetime


class JSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        elif isinstance(o, unicode):
            return str(o)
        elif isinstance(o, datetime.datetime):
            return o.isoformat()

        return super(JSONEncoder, self).default(o)
