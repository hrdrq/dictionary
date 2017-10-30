# encoding: utf-8

import sys
import os
import datetime
import json
import re
import time

import boto3
import requests

sys.path.append('../')
from utils import connect_db
from .db_tables import DictJA, DictJADetail
from credentials import *

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}


in_lambda = False

s = requests.Session()


def login():
    print("login()")

    def set_environ():
        print("set_environ()")
        for cookie in s.cookies:
            if cookie.name == 'sessionid':
                if in_lambda:
                    clientLambda = boto3.client("lambda")
                    clientLambda.update_function_configuration(
                        FunctionName='rhinospike_worker',
                        Environment={
                            'Variables': {
                                'sessionid': cookie.value,
                                'expires': str(cookie.expires)
                            }
                        }
                    )
                else:
                    os.environ['sessionid'] = cookie.value
                    os.environ['expires'] = str(cookie.expires)

    def login_req():
        print("login_req()")
        s.post(url="https://rhinospike.com/account/login/",
               data={
                   "username": RHINOSPIKE_USER,
                   "password": RHINOSPIKE_PW,
                   "remember": "on"
               },
               headers=headers)
        set_environ()

    def update_cookies():
        print("update_cookies()")
        s.cookies.update({
            "sessionid": os.environ['sessionid']
        })

    if os.environ.get('sessionid', '') != '' and os.environ.get('expires', '') != '':
        expires_dt = datetime.datetime.fromtimestamp(
            int(os.environ['expires']))
        after_10_sec = datetime.datetime.now() + datetime.timedelta(seconds=10)
        print("after_10_sec:", after_10_sec)
        print("expires_dt:", expires_dt)
        if expires_dt < after_10_sec:
            login_req()
        else:
            update_cookies()
    else:
        login_req()


def add_sentence(sentence):
    res = s.post(url="https://rhinospike.com/new/audio_request/?return=https://rhinospike.com/home/",
                 data={
                     "phonenumber": "",
                     "title": sentence,
                     "lang": "jpn",
                     "notes": "",
                     "text": sentence,
                     "tags": "",
                     "action": "create",
                     "lang_checked": "0"
                 },
                 headers=headers)
    if res.text.find('Successfully submitted article') > -1:
        return True
    else:
        return False


def example_to_plain(example):
    example = re.sub(r'\[.+?\]', '', example)
    example = example.replace(' ', '').replace(
        '<b>', '').replace('</b>', '').replace('<br>', '\n')
    return example


def main():
    sql = connect_db()
    res = sql.query(DictJADetail).filter((DictJADetail.example !=
                                          None) & (DictJADetail.need_add_example_audio == True)).limit(3)
    if res:
        login()
        for r in res:
            example = example_to_plain(r.example)
            print(example)
            if add_sentence(example):
                r.need_add_example_audio = False
                sql.commit()
            time.sleep(3)
    # login()


def add_sentence_one_time(sentence):
    login()
    return add_sentence(example_to_plain(sentence))


def lambda_handler(event, context):
    print('lambda_handler()')
    global in_lambda
    in_lambda = True
    main()

if __name__ == '__main__':
    main()
    # add_sentence("相性がいい")
