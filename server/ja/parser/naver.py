# encoding: utf-8

import requests
import re
import lxml
from pyquery import PyQuery

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}


class Naver(object):
    URL = 'http://jpdic.naver.com/search.nhn?range=word&q="{word}"'
    EXAMPLE_URL = 'http://jpdic.naver.com/search.nhn?range=example&q={word}'

    def search(self, word):
        response = requests.get(self.URL.format(word=word), headers=headers)
        doc = PyQuery(response.text)
        results = []
        for item in doc("div.srch_top"):
            # result = {}
            item = PyQuery(item)
            url = item('span.player')('button.play').attr('data-purl')
            if url:
                _word = ''
                for s in item('span.jp'):
                    s = PyQuery(s)
                    _word += s.text()
                for u in url.split('|'):
                    results.append({
                        'word': _word,
                        'url': u
                    })
                # match = re.compile(r"(http.*)(\|(http.*)?)?").search(url)
                # if match:
                #     # url = match.group(1)
                #     print(match.group(1))
                #     print(match.group(2))
                #     print(match.group(3))
                #     results.append({
                #         'word': _word,
                #         'url': match.group(1)
                #     })
                #     if match.group(3):
                #         results.append({
                #             'word': _word,
                #             'url': match.group(3)
                #         })

                # result['url'] = url
                # for s in item('span.jp'):
                #     s = PyQuery(s)
                #     result['word'] = result.get('word', '') + s.text()
                # results.append(result)

        if results:
            return {"status": 'success', "results": results}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}

    def example(self, word):

        def parse_span(span):
            result = ""
            span = PyQuery(span)
            children_span_or_strong = span.children('span,strong')
            children_ruby = span.children('ruby')
            if span.is_('strong'):
                return "<b>" + span.text().replace(' ', '') + "</b>"
            elif children_span_or_strong:
                for cs in children_span_or_strong:
                    result += parse_span(cs)
            elif children_ruby:
                for cr in children_ruby:
                    cr = PyQuery(cr)
                    # strong = True if cr.find('strong') else False

                    r = " {kanji}[{kana}]".format(
                        kanji=cr('rb').text().replace(' ', ''), kana=cr('rt').text().replace(' ', ''))
                    if cr.find('strong'):
                        r = "<b>" + r + "</b>"
                    result += r
            else:
                r = span.text()
                # print(r)
                if span.find('strong'):
                    r = "<b>" + r + "</b>"
                result = r
            return result
        response = requests.get(
            self.EXAMPLE_URL.format(word=word), headers=headers)
        # f = open('y.html', 'r')
        # f = open('y.html', 'w')
        # f.write(response.text)
        # text = f.read()
        text = response.text
        doc = PyQuery(text)
        results = []
        for item in doc("li.inner_lst"):
            result = {}
            # print(lxml.etree.ElementTree.tostring(
            #     item, encoding='utf8', method='html'))
            # item = re.sub(r'\[.+?\]', '', item)
            # print(item)
            item = PyQuery(item)
            item_html = item.outerHtml()
            item = PyQuery(re.sub(r'\[.+?\]', '', item_html))
            # print(item_html)
            sentence_element = item('p').eq(0)('span').eq(0)
            sentence = ""
            for part in sentence_element.contents():
                if isinstance(part, lxml.etree._ElementUnicodeResult):
                    sentence += str(part)
                else:
                    sentence += parse_span(part)
                # big_part = PyQuery(big_part)
                # for part in big_part.children('span'):
                #     sentence += parse_span(part)
                #     # part = PyQuery(part)
                #     # part_result = ""
                #     # strong = False
                #     # if part.find('strong'):
                #     #     strong = True
                #     # ruby = part('ruby')
                #     # if ruby:
                #     #     part_result = " {kanji}[{kana}]".format(
                #     #         kanji=ruby('rb').text(), kana=ruby('rt').text())
                #     # else:
                #     #     part_result = part.text()
                #     # if strong:
                #     #     part_result = "<b>" + part_result + "</b>"
                #     # sentence += part_result
            result['sentence'] = sentence
            sentence_element.find('rp,rt').remove()
            sentence_plain = sentence_element.text()

            # m = re.search(r"\[(.+?)\]", sentence_plain)
            # if m:
            #     result['sentence'] = result['sentence'].replace(
            #         m.group(1).replace(' ', ''), '')
            # sentence_plain = re.sub(r'\[.+?\]', '', sentence_plain)
            # sentence_plain = re.sub(
            #     r'\( (.+?) \)', r'', sentence_plain)
            result['sentence_plain'] = sentence_plain.replace(' ', '')

            sentence_element.find('strong').text('＿')
            listening_hint = sentence_element.text()
            # listening_hint = re.sub(r'\[.+?\]', '', listening_hint)
            # listening_hint = re.sub(
            #     r'\( (.+?) \)', r'', listening_hint)

            listening_hint = listening_hint.replace(' ', '')
            result['listening_hint'] = re.sub(r'＿+', r'＿', listening_hint)
            results.append(result)
            # sentence = re.sub(r'\[.*\]', '', sentence)
            # result['sentence_furigana'] = re.sub(
            #     r' \( (.+?) \) ', r'[\g<1>]', sentence)
            # # print(sentence.text())
            # results.append(result)
        if results:
            return {"status": 'success', "results": results, "type": "naver"}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}
