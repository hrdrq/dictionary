# encoding: utf-8

import requests
import re

import jaconv

# test = {
#     "api_version": "0.0.2",
#     "matched_ngrams": [
#         "捥ぎ取る",
#         "捥ぎ取ら"
#     ],
#     "ngram": "捥ぎ取る",
#     "sentences": [
#         {
#             "properties": {
#                 "mecab_output": "艦\t名詞,一般,*,*,*,*,艦,カン,カン 尾\t名詞,一般,*,*,*,*,尾,オ,オ 部分\t名詞,一般,*,*,*,*,部分,ブブン,ブブン は\t助詞,係助詞,*,*,*,*,は,ハ,ワ 第\t接頭詞,数接続,*,*,*,*,第,ダイ,ダイ 205\t名詞,数,*,*,*,*,* 肋材\t名詞,一般,*,*,*,*,肋材,ロクザイ,ロクザイ まで 助詞,副助詞,*,*,*,*,まで,マデ,マデ 事実\t名詞,副詞可能,*,*,*,*,事実,ジジツ,ジジツ 上\t名詞,接尾,副詞可能,*,*,*,上,ジョウ,ジョー 捥\t名詞,一般,*,*,*,*,* ぎ\t名詞,一般,*,*,*,*,* 取ら\t動詞,自立,*,*,五段・ラ行,未然形,取る,トラ,トラ れ\t動詞,接尾,*,*,一段,連用形,れる,レ,レ 、\t記号,読点,*,*,*,*,、,、,、 辛うじて\t副詞,一般,*,*,*,*,辛うじて,カロウジテ,カロージテ 外\t名詞,一般,*,*,*,*,外,ソト,ソト 板\t名詞,接尾,一般,*,*,*,板,バン,バン の\t助詞,連体化,*,*,*,*,の,ノ,ノ 一部\t名詞,副詞可能,*,*,*,*,一部,イチブ,イチブ で\t助詞,格助詞,一般,*,*,*,で,デ,デ ぶら下がっ 動詞,自立,*,*,五段・ラ行,連用タ接続,ぶら下がる,ブラサガッ,ブラサガッ て\t助詞,接続助詞,*,*,*,*,て,テ,テ いる\t動詞,非自立,*,*,一段,基本形,いる,イル,イル 状態\t名詞,一般,*,*,*,*,状態,ジョウタイ,ジョータイ で\t助動詞,*,*,*,特殊・ダ,連用形,だ,デ,デ あっ\t助動詞,*,*,*,五段・ラ行アル,連用タ接続,ある,アッ,アッ た\t助動詞,*,*,*,特殊・タ,基本形,た,タ,タ 。\t記号,句点,*,*,*,*,。,。,。 EOS",
#                 "next_sentence": "火災も発生した。",
#                 "prev_sentence": "のちに明らかにされたところによれば、これはソナーを搭載した自動誘導式の魚雷で、ドイツ海軍のUボートVII型U293から発射されたものであった。"
#             },
#             "sentence": "艦尾部分は第205肋材まで事実上捥ぎ取られ、辛うじて外板の一部でぶら下がっている状態であった。",
#             "source": "jawiki-20141211",
#             "title": ""
#         },
#         {
#             "properties": {
#                 "mecab_output": "士官\t名詞,一般,*,*,*,*,士官,シカン,シカン の\t助詞,連体化,*,*,*,*,の,ノ,ノ 船室\t名詞,一般,*,*,*,*,船室,センシツ,センシツ で\t助詞,格助詞,一般,*,*,*,で,デ,デ は\t助詞,係助詞,*,*,*,*,は,ハ,ワ シャンデリア\t名詞,一般,*,*,*,*,シャンデリア,シャンデリア,シャンデリア が\t助詞,格助詞,一般,*,*,*,が,ガ,ガ 捥\t名詞,一般,*,*,*,*,* ぎ\t名詞,一般,*,*,*,*,* 取ら\t動詞,自立,*,*,五段・ラ行,未然形,取る,トラ,トラ れ\t動詞,接尾,*,*,一段,連用形,れる,レ,レ 、\t記号,読点,*,*,*,*,、,、,、 家具\t名詞,一般,*,*,*,*,家具,カグ,カグ が\t助詞,格助詞,一般,*,*,*,が,ガ,ガ 運び出さ\t動詞,自立,*,*,五段・サ行,未然形,運び出す,ハコビダサ,ハコビダサ れ\t動詞,接尾,*,*,一段,連用形,れる,レ,レ た\t助動詞,*,*,*,特殊・タ,基本形,た,タ,タ 。\t記号,句点,*,*,*,*,。,。,。 EOS",
#                 "next_sentence": "アフトローイルの士官集会室にあったはずのたて型ピアノは、やがてイギリス巡洋艦上で発見された。",
#                 "prev_sentence": "イギリス水兵らは両艦の居住区画の捜査を行った際、欲しいと思ったものはすべて、衣類やシーツ類、筆記用具といった士官個人の身の回りの品に至るまで何でも持ち去った。"
#             },
#             "sentence": "士官の船室ではシャンデリアが捥ぎ取られ、家具が運び出された。",
#             "source": "jawiki-20141211",
#             "title": ""
#         },
#         {
#             "properties": {
#                 "mecab_output": "レッドキング\t名詞,固有名詞,一般,*,*,*,レッドキング,レッドキング,レッドキング により\t助詞,格助詞,連語,*,*,*,により,ニヨリ,ニヨリ 翼\t名詞,一般,*,*,*,*,翼,ツバサ,ツバサ を\t助詞,格助詞,一般,*,*,*,を,ヲ,ヲ 捥\t名詞,一般,*,*,*,*,* ぎ\t名詞,一般,*,*,*,*,* 取ら\t動詞,自立,*,*,五段・ラ行,未然形,取る,トラ,トラ れ\t動詞,接尾,*,*,一段,連用形,れる,レ,レ 弱体\t名詞,形容動詞語幹,*,*,*,*,弱体,ジャクタイ,ジャクタイ 化\t名詞,接尾,サ変接続,*,*,*,化,カ,カ し\t動詞,自立,*,*,サ変・スル,連用形,する,シ,シ た\t助動詞,*,*,*,特殊・タ,基本形,た,タ,タ ドラコ 名詞,一般,*,*,*,*,* 相手\t名詞,一般,*,*,*,*,相手,アイテ,アイテ で\t助詞,格助詞,一般,*,*,*,で,デ,デ も\t助詞,係助詞,*,*,*,*,も,モ,モ やはり 副詞,一般,*,*,*,*,やはり,ヤハリ,ヤハリ 苦戦\t名詞,サ変接続,*,*,*,*,苦戦,クセン,クセン し\t動詞,自立,*,*,サ変・スル,連用形,する,シ,シ 、\t記号,読点,*,*,*,*,、,、,、 業\t名詞,一般,*,*,*,*,業,ゴウ,ゴー を\t助詞,格助詞,一般,*,*,*,を,ヲ,ヲ 煮やし\t動詞,自立,*,*,五段・サ行,連用形,煮やす,ニヤシ,ニヤシ た\t助動詞,*,*,*,特殊・タ,基本形,た,タ,タ レッドキング\t名詞,固有名詞,一般,*,*,*,レッドキング,レッドキング,レッドキング と 助詞,並立助詞,*,*,*,*,と,ト,ト 最終\t名詞,一般,*,*,*,*,最終,サイシュウ,サイシュー 的\t名詞,接尾,形容動詞語幹,*,*,*,的,テキ,テキ に\t助詞,格助詞,一般,*,*,*,に,ニ,ニ は\t助詞,係助詞,*,*,*,*,は,ハ,ワ 二\t名詞,数,*,*,*,*,二,ニ,ニ 匹\t名詞,接尾,助数詞,*,*,*,匹,ヒキ,ヒキ がかり\t名詞,接尾,一般,*,*,*,がかり,ガカリ,ガカリ で\t助詞,格助詞,一般,*,*,*,で,デ,デ ドラコ\t名詞,一般,*,*,*,*,* を\t助詞,格助詞,一般,*,*,*,を,ヲ,ヲ 倒す\t動詞,自立,*,*,五段・サ行,基本形,倒す,タオス,タオス 。\t記号,句点,*,*,*,*,。,。,。 EOS",
#                 "next_sentence": "ドラコ絶命後はレッドキングと戦うも一方的に痛めつけられ、全く敵わず逃亡する。",
#                 "prev_sentence": "飛来したドラコと戦うが苦戦気味で、途中で乱入してきたレッドキングに恐れをなし、一時的にレッドキングと手を組み二対一でドラコと戦う。"
#             },
#             "sentence": "レッドキングにより翼を捥ぎ取られ弱体化したドラコ相手でもやはり苦戦し、業を煮やしたレッドキングと最終的には二匹がかりでドラコを倒す。",
#             "source": "jawiki-20141211",
#             "title": ""
#         }
#     ]
# }


class Yourei(object):
    URL = 'http://yourei.jp/api/?action=getsentenceswithpropsourcetitle&n={count}&start={offset}&match_type=lemma&ngram={word}'

    def search(self, word, count=20, offset=1):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
        response = requests.get(self.URL.format(
            word=word, count=count, offset=offset), headers=headers)
        data = response.json()
        # data = test
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
                # print(repr(mecab_output))
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
                        # sentence = sentence.replace(
                        #     k, ' {kanji}[{kana}]'.format(kanji=k, kana=v))
                        start_index = sentence.find(kanji, working_index)
                        end_index = start_index + len(kanji)
                        to_insert = " {}[{}]".format(kanji, kana)
                        sentence = sentence[:start_index] + \
                            to_insert + sentence[end_index:]
                        working_index = start_index + len(to_insert)

                result['sentence'] = sentence
                results.append(result)

            return {"status": 'success', "results": results, "type": "yourei"}
