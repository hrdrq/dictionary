# encoding: utf-8

import logging
import re
from sqlalchemy import create_engine, func, or_, and_
from sqlalchemy.orm import sessionmaker, aliased
import time

# from .parser.weblio import Weblio
# from .parser.hujiang import Hujiang
from parser.yourei import Yourei
# from .parser.forvo import Forvo
from db_tables import DictJA, DictJADetail, Example
# import tables
import sys
sys.path.append('../')
from utils import result_parse, connect_db


logger = logging.getLogger()
logger.setLevel(logging.INFO)

if __name__ == '__ma__':
    s = connect_db()
    res = s.query(Example).all()
    for r in res:
        new = re.sub(r'＿+', r'＿', r.listening_hint)
        if new != r.listening_hint:

            print(new,r.listening_hint)
            r.listening_hint = new
            s.commit()
    s.close()

def div_to_p():
    s = connect_db()
    res = s.query(DictJADetail).filter(DictJADetail.id>=9418).filter(DictJADetail.examples != None).all()
    for r in res:
        print(r.id, r.kana)
        # print(r.examples)
        r.examples = re.sub(r'<div class="ex">(.*?)<\/div>', r'<p>\g<1></p>', r.examples)
        s.commit()


if __name__ == '__main__':
    div_to_p()
    sys.exit()
    s = connect_db()
    y = Yourei()
    # res = s.query(DictJA).filter(DictJA.type == "normal").filter(DictJA.id>=15448).all()
    # res = s.query(DictJA).filter(DictJA.id>=9551).filter(DictJA.type == "normal").filter(DictJA.detail.has(example=None)).all()
    res = s.query(DictJA).filter(DictJA.id>18732).filter(DictJA.type == "normal").filter((DictJA.has_updated == True) | DictJA.detail.has(example=None)).all()
    for r in res:
        print(r.id, r.word)
        data = y.search(r.word,11)
        if data['status'] == 'success':
            results = data['results']
            examples = ''
            for i, e in enumerate(results):
                if i == 0:
                    r.detail.example=e['sentence']
                    r.detail.listening_hint=e['listening_hint']
                else:
                    examples += '<div class="ex">{}</div>'.format(e['sentence'])
            if examples != '':
                r.detail.examples = examples
            r.has_updated=True
            r.detail.need_add_example_audio=2
            s.commit()
            print('y')
        time.sleep(2)
    s.close()