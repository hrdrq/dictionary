from __future__ import print_function
import os
import asyncio
import base64
from io import BytesIO

from PIL import Image
import requests
from io import BytesIO

import sys
sys.path.append('../../')
from credentials import GCS_KEY, GCS_CX

async def queue_execution(arg_urls, callback, parallel=2):
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    for u in arg_urls:
        queue.put_nowait(u)

    async def fetch(q):
        def do_req():
            return 
        while not q.empty():
            u = await q.get()
            future = loop.run_in_executor(None, requests.get, u)
            future.add_done_callback(callback)
            await future

    tasks = [fetch(queue) for i in range(parallel)]
    return await asyncio.wait(tasks)


def image_search(word):

    # try:
    response = requests.get(
        'https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&searchType=image&q={word}&hl=ja'.format(key=GCS_KEY, cx=GCS_CX, word=word))
    urls = [i['link'] for i in response.json()['items']]

    # loop = asyncio.get_event_loop()

    # results = []

    # def store_result(f):
    #     results.append(f.result())
    # loop.run_until_complete(queue_execution(urls, store_result))

    async def do_request():
        results = []
        loop = asyncio.get_event_loop()
        for url in urls:
            def do_req():
                try:
                    return requests.get(url, timeout=3)
                except:
                    return None
            req = loop.run_in_executor(
                None, do_req)
            res = await req
            results.append(res)
        return results
            
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(do_request())

    buffered = BytesIO()
    img_result = Image.new("RGB", (360, 360))

    index = 0
    for r in results:
        # path = os.path.expanduser(file)
        # res = requests.get(url)
        # print(r.status_code, r.url)
        if not r or r.status_code != 200:
            continue
        try:
            img = Image.open(BytesIO(r.content))
        except Exception as e:
            print("Image.open例外:", e.args)
            continue
        # img = Image.open("4.png")
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
        # img.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
        img.thumbnail((120, 120), Image.ANTIALIAS)
        x = index // 3 * 120
        y = index % 3 * 120
        w, h = img.size
        print('pos {0},{1} size {2},{3}'.format(x, y, w, h))
        img_result.paste(img, (x, y, x + w, y + h))
        index += 1

    # img_result.save('image3.jpg')
    img_result.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('ascii')
    # print(img_str)
    return {"status": 'success', "result": img_str}

    # except:
    #     return {"status": 'error', "error_detail": ""}