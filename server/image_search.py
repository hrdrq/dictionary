# -*- coding: utf-8 -*-
import base64
import threading
from io import BytesIO

from PIL import Image
import requests

from credentials import GCS_KEY, GCS_CX

import pdb
d = pdb.set_trace

def image_search(word, lang='ja'):

    url = 'https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&searchType=image&q={word}&hl={lang}'.format(key=GCS_KEY, cx=GCS_CX, word=word, lang=lang) 

    res = requests.get(url)
    urls = [i['image']['thumbnailLink'] for i in res.json()['items']]
    
    results = []
    def get(url):
        try:
            results.append(requests.get(url, timeout=5))
        except:
            results.append(None)
    threads = [threading.Thread(target=get, args=(url,)) for url in urls]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    buffered = BytesIO()
    img_result = Image.new("RGB", (360, 360))

    index = 0
    for r in results:
        if not r or r.status_code != 200:
            continue
        try:
            img = Image.open(BytesIO(r.content))
        except Exception as e:
            print("Image.open Error:", e.args)
            continue
        width, height = img.size

        if width > height:
            delta = width - height
            left = int(delta / 2)
            upper = 0
            right = height + left
            lower = height
        else:
            delta = height - width
            left = 0
            upper = int(delta / 2)
            right = width
            lower = width + upper

        img = img.crop((left, upper, right, lower))
        # img.thumbnail((120, 120), Image.ANTIALIAS)
        img = img.resize((120, 120), Image.ANTIALIAS)
        x = index // 3 * 120
        y = index % 3 * 120
        w, h = img.size
        # print('pos {0},{1} size {2},{3}'.format(x, y, w, h))
        img_result.paste(img, (x, y, x + w, y + h))
        index += 1

    img_result.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('ascii')
    return {"status": 'success', "result": img_str}

