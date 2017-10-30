# encoding: utf-8

import requests
import re
from pyquery import PyQuery


class Hujiang(object):
    URL = 'http://dict.hjenglish.com/kr/{word}'
    UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36")

    def search(self, word):
        response = requests.get(self.URL.format(
            word=word), headers={'User-Agent': self.UA})
        doc = PyQuery(response.text)
        results = []
        for item in doc("div#kr_Result_panel"):
            print(item)
            result = {'word': word}
            item = PyQuery(item)
            # result['kanji'] = item("span.jpword").text()
            # result['kana'] = item("span[title=假名]").text()
            content = item("div.word_ext_con")
            content("a").remove()
            # content("script").remove()
            content("img").remove()
            content("span.hide").remove()
            # content("div#shift_content").remove()
            # content("div.recommend_box").remove()
            content("iframe").remove()
            for c in content('*'):
                c = PyQuery(c)
                c.removeAttr('class').removeAttr(
                    'title').removeAttr('id').removeAttr('style')
                # style = c.attr('style')
                # if style == 'color:#333333;' or style == 'margin-top:10px;' or style == 'display: none':
                #     c.removeAttr('style')
                # if style == 'padding-left:20px; font-size: 13px;':
                #     c.attr("style", "padding-left:5%;font-size:80%;")
                # if c.attr("src") == "http://dict.hjenglish.com/images/icon_star.gif":
                #     c.after('<span class="star_img"></span>')
                #     c.remove()
                # if c.is_("ul"):
                #     c.addClass("chinese")

            result['meaning'] = content.html().replace('&#13;', '').replace(
                '<!--详细释义-->', '').replace('<!--词形变化-->', '')
            results.append(result)

        if results:
            return {"status": 'success', "results": results}
        else:
            return {"status": 'error', "error_detail": "Nothing found."}
