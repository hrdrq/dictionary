# encoding: utf-8
# YサイトのAPIを使って、例文を取得する

import requests
import re

import jaconv

class Yourei(object):
    URL = 'http://yourei.jp/api/?action=getsentenceswithpropsourcetitle&n={count}&start={offset}&match_type=lemma&ngram={word}'

    def search(self, word, count=20, offset=1):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
        response = requests.get(self.URL.format(
            word=word, count=count, offset=offset), headers=headers)
        data = response.json()
        if not data['sentences']:
            return {"status": 'error', "error_detail": "Nothing found."}
        else:
            matched_ngrams = data['matched_ngrams']
            re_pattern = '(' + ('|'.join(matched_ngrams)) + ')'
            results = []
            for s in data['sentences']:
                sentence = s['sentence']
                result = {
                    "sentence_plain": sentence,
                    "listening_hint": re.sub(re_pattern, "＿", sentence)
                }
                sentence = re.sub(re_pattern, "<b>\g<1></b>", sentence)

                mecab_output = s['properties']['mecab_output']
                kanji_dict_list = []
                for m in mecab_output.split('\n'):
                    k_v = m.split('\t')
                    if len(k_v) == 2 and re.match("[一-龥]", k_v[0]):
                        mecab_detail = (k_v[1]).split(",")
                        if len(mecab_detail) > 7:
                            _word = k_v[0]
                            _kana = jaconv.kata2hira(mecab_detail[7])
                            match = re.search("[一-龥]([^一-龥]+?)$", _word)
                            if match:
                                remove_index = match.start(1) - len(_word)
                                _word = _word[:remove_index]
                                _kana = _kana[:remove_index]
                            kanji_dict_list.append({_word: _kana})
                working_index = 0
                for d in kanji_dict_list:
                    for kanji, kana in d.items():
                        start_index = sentence.find(kanji, working_index)
                        end_index = start_index + len(kanji)
                        to_insert = " {}[{}]".format(kanji, kana)
                        sentence = sentence[:start_index] + \
                            to_insert + sentence[end_index:]
                        working_index = start_index + len(to_insert)

                result['sentence'] = sentence
                results.append(result)

            return {"status": 'success', "results": results}
