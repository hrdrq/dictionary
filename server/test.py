# encoding: utf-8
from __future__ import print_function, unicode_literals
import json
import csv

from utils import JSONEncoder
from search_handler import search_handler, Query
from save_handler import save_handler, Save
from suggest_handler import suggest_handler, Suggest
from main import handle

def basic_test():
    get_test = {
        'method': 'GET',
        'headers': {
            'content-type': 'application/json',
        },
        'path': '/ja/save/query',
        'queryParams': {
            "kana": "てすと"
        },
        'body': {
        }
    }
    post_test = {
        'method': 'POST',
        'headers': {
            'content-type': 'application/json',
        },
        'path': '/ja/save',
        'queryParams': {
        },
        'body': {
            "word": "真剣",
            "accent": "0",
            "kana": "しんけん",
            "meaning": ' <div> <span style="border-radius:0.4em;color:white;background-color:black;padding:0 0.3em;margin:2px;font-weight:normal;font-size:90%;">一</span> （ 名 ） <div> <div> <div> （木刀や竹刀<span style="font-size:75%">（しない）</span>でなく）本物の刀。 「 －で立ち合う」 </div> </div> </div> </div> <div style="margin-top:1em;"> <span style="border-radius:0.4em;color:white;background-color:black;padding:0 0.3em;margin:2px;font-weight:normal;font-size:90%;">二</span> （ 形動 ） <span style="font-size:75%">［文］ ナリ </span> <div> <div> <div> 一生懸命に物事をするさま。本気であるさま。 「 －に取り組む」 「 －な態度」 </div> </div> </div> <div style="margin-left:1em;"><span style="color:#006666;font-weight:bold;">［派生］</span> －さ （ 名 ） －み （ 名 ） </div> </div> ',
            'chinese': 'asfasfa'
        }
    }
    post_test2 = {
        'method': 'POST',
        'headers': {
            'content-type': 'application/json',
        },
        'path': '/ja/save/add_alternative_word',
        'queryParams': {
        },
        'body': {
            "word": "しんけん",
            "detail_id": 2,
        }
    }
    return save_handler(get_test)
    
COL = [
    'word',
    'meaning',
    'chinese',
    'kana',
    'gogen',
    'accent',
    'tag'
]
def update_test():
    query = Query()
    save = Save()

    f = open('to_update.csv', 'r')
    reader = csv.reader(f)
    for row in reader:
        req = {'type': 'collect'}
        for idx, val in enumerate(row):
            if idx != 6 and val != '':
                req[COL[idx]] = val.decode('utf-8')
        print(req['word'])
        res = query.search(req.pop('word'))
        if res['status'] != 'need_update':
            return 'error'
        req['id'] = res['id']
        
        save.update(req)

def test():
    save = Save()
    data = {"kana":"ひとつ","accent":"2","meaning":"<div><span style=\"border-radius:0.4em;color:white;background-color:black;padding:0 0.3em;margin:2px;font-weight:normal;font-size:90%;\">一</span> （ 名 ）<div><div><div><div style=\"float:left\">①</div><div style=\"margin-left:1em;\">いち。一個。物の数を数えるときに使う。 「 －，ふたつ」</div></div><div><div style=\"float:left\">②</div><div style=\"margin-left:1em;\">一歳。 「 －年を取る」</div></div><div><div style=\"float:left\">③</div><div style=\"margin-left:1em;\">同じであること。区別がないこと。<div><div style=\"float:left\">㋐</div><div style=\"margin-left:1em;\">同一の物・場所であること。 「 －もの」 「 －ところ」</div></div><div><div style=\"float:left\">㋑</div><div style=\"margin-left:1em;\">同じ状態であること。あたかも単一のものであるかのような状態を示すこと。 「世界は－」 「全員が－にまとまる」</div></div></div></div><div><div style=\"float:left\">④</div><div style=\"margin-left:1em;\">それに属する一種。そのうちの一種と考えてよいもの。 「それも－の方法だ」 「施策の－といえる」</div></div><div><div style=\"float:left\">⑤</div><div style=\"margin-left:1em;\">名詞の下に付けて，限定または強調したり，最低または最少の例としてあげ，他を類推させるときに用いる。 「身－で来る」 「塵－落ちていない」 「挨拶<span style=\"font-size:75%\">（あいさつ）</span>－満足にできない」 「何－残さない」 「どれ－として満足なものはない」</div></div><div><div style=\"float:left\">⑥</div><div style=\"margin-left:1em;\">そうすることによって決まる，それ次第であることを強調していうときに用いる。 「やるかやめるか決心－だ」 「心の持ちよう－でどうにでも変わる」</div></div><div><div style=\"float:left\">⑦</div><div style=\"margin-left:1em;\">箇条書きの文書で，各条の初めにつける語。 「 －，軍人は忠節を尽くすを本分とすべし」</div></div><div><div style=\"float:left\">⑧</div><div style=\"margin-left:1em;\">容器に一杯。酒・水などにいう。 「酒<span style=\"font-size:75%\">（しゆ）</span>を－持ちて候／謡曲・一角仙人」</div></div><div><div style=\"float:left\">⑨</div><div style=\"margin-left:1em;\">昔の時刻で，一刻を四つに分けた第一。 「子<span style=\"font-size:75%\">（ね）</span>－」</div></div></div></div></div><div style=\"margin-top:1em;\"><span style=\"border-radius:0.4em;color:white;background-color:black;padding:0 0.3em;margin:2px;font-weight:normal;font-size:90%;\">二</span> （ 副 ）<div><div><div>流れに区切りをつけて，新しい事態とみなして対応する気持ちを表す。人を誘ったり，決意したりするときなどに用いる。 「今夜は－盛大にやってくれ」 「ここは－慎重に行こう」 〔何かを頼む場合，それが軽い物事であることを強調する気持ちを込めて用いる。「－穏便に願います」〕</div></div></div></div><div style=\"margin-top:1em;\"><div style=\"float:left;\"><span style=\"color:#006666;font-weight:bold;\">［句］</span></div><div style=\"margin-left:2em;\"><span class=\"NetDicItemLink\">一つ穴の狢</span> ・ <span class=\"NetDicItemLink\">一つとして</span> ・ <span class=\"NetDicItemLink\">一つなる</span> ・ <span class=\"NetDicItemLink\">一つになる</span> ・ <span class=\"NetDicItemLink\">一つ間違えば</span> ・ <span class=\"NetDicItemLink\">一つ屋根の下に住む</span></div></div>","chinese":"<div><br></div><div><ul class=\"chinese\"><li><div style=\"margin-top:5px;\">名词</div></li><li><br><ul class=\"chinese\"><li><div><span>1</span>. <span>【副】 ;名（1）一个；一人；一岁（1個；1歳）</span></div><div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\">それも<strong><strong>一つ</strong></strong>の考えだ</span></div><div style=\"padding-left:16px; line-height:24px;\">那也是一个主意。</div></div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\">まちがいは<strong><strong>一つ</strong></strong>もなかった</span></div><div style=\"padding-left:16px; line-height:24px;\">一点儿错误也没有。</div></div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\">彼には<strong><strong>一つ</strong></strong>としてとりえがない</span></div><div style=\"padding-left:16px; line-height:24px;\">他毫无长处。</div></div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\"><strong><strong>一つ</strong></strong>のすいかを5人で食べた</span></div><div style=\"padding-left:16px; line-height:24px;\">五个人吃了一个西瓜。</div></div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\">誕生日がきて<strong><strong>一つ</strong></strong>になる</span></div><div style=\"padding-left:16px; line-height:24px;\">到生日就一岁了。</div></div></div></li><li><div><span>2</span>. <span>一项；第一（1項目）。</span></div><div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\"><strong><strong>一つ</strong></strong>、酒を飲まないこと。ふたつ、かけごとをしないこと</span></div><div style=\"padding-left:16px; line-height:24px;\">第一，不许饮酒。第二、不许赌博。</div></div></div></li><li><div><span>3</span>. <span>相同；一样〔同じ〕。</span></div><div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\">世界は<strong><strong>一つ</strong></strong></span></div><div style=\"padding-left:16px; line-height:24px;\">世界大同。</div></div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\">ふたりの気持ちが<strong><strong>一つ</strong></strong>になる</span></div><div style=\"padding-left:16px; line-height:24px;\">两个人的心情一样。</div></div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\">表現はちがうが内容は<strong><strong>一つ</strong></strong>だ</span></div><div style=\"padding-left:16px; line-height:24px;\">表现方法虽然不同，内容是一样的。</div></div></div></li><li><div><span>4</span>. <span>一方面〔いっぽう〕。</span></div><div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\">旅行に行かないのは、<strong><strong>一つ</strong></strong>には時間がかかるし、<strong><strong>一つ</strong></strong>には金がないからだ</span></div><div style=\"padding-left:16px; line-height:24px;\">不去旅行，一个原因是费时间，另一个原因是没有钱。</div></div></div></li><li><div><span>5</span>. <span>连。只〔ひとつさえ〕。</span></div><div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\">彼女はみそ汁<strong><strong>一つ</strong></strong>満足につくれない</span></div><div style=\"padding-left:16px; line-height:24px;\">她连大酱汤都做不好。</div></div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\">努力<strong><strong>一つ</strong></strong>で成功する</span></div><div style=\"padding-left:16px; line-height:24px;\">只要努力就能成功。</div></div></div></li><li><div><span>6</span>. <span>副（1）试一试；稍微（すごしい）。</span></div><div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\"><strong><strong>一つ</strong></strong>やって見よう</span></div><div style=\"padding-left:16px; line-height:24px;\">试试看。</div></div><div style=\"padding-bottom:4px;\"><div><span style=\"line-height:24px;\"><strong><strong>一つ</strong></strong>いかがですか</span></div><div style=\"padding-left:16px; line-height:24px;\">啊，怎么样？</div></div></div></li></ul></li></ul></div>","id":1}
    return save.update(data)

def suggest_test():
    # suggest = Suggest()
    # return suggest.search('ひと')

    get_test = {
        'method': 'GET',
        'headers': {
            'content-type': 'application/json',
        },
        'path': '/ja/suggest',
        'queryParams': {
            "word": "てすと"
        },
        'body': {
        }
    }
    return suggest_handler(get_test)

def main_test():
    get_test = {
        'method': 'GET',
        'headers': {
            'content-type': 'application/json',
        },
        'path': '/ja/suggest',
        'queryParams': {
            "word": "てすと"
        },
        'body': {
        }
    }
    return handle(get_test, None)

if __name__ == '__main__':
    res = main_test()
    # res = basic_test()
    # res = update_test()
    print(json.dumps(res, indent=4, ensure_ascii=False, cls=JSONEncoder))