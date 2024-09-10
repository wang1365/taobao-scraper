import json
from datetime import datetime

from app.cache import save_to_cache
from urllib.parse import urlparse, parse_qs


def on_response(url, text):
    print(f'{datetime.now()} Response: {url} Status: {text}')

    # 店铺商品列表API - 首页
    if 'mtop.taobao.shop.simple.fetch' in url:
        parsed_url = urlparse(url)
        qs = parse_qs(parsed_url.query)
        info = json.loads(qs['data'][0])
        shop_id = info['shopId']
        print('===>', qs)
        data = json.loads(text)
        with open('./out/data/products.txt', 'a', encoding='utf-8') as f:
            for product in data['data']['itemInfoDTO']['data']:
                f.write(product['itemUrl'] + '\n')

    # 店铺商品列表API
    if 'mtop.taobao.shop.simple.item.fetch' in url:
        parsed_url = urlparse(url)
        qs = parse_qs(parsed_url.query)
        info = json.loads(qs['data'][0])
        shop_id = info['shopId']
        print('===>', qs)
        data = json.loads(text)
        with open('./out/data/products.txt', 'a', encoding='utf-8') as f:
            for product in data['data']['data']:
                f.write(product['itemUrl'] + '\n')
        # save_to_cache(text, shop_id)
    # save_to_cache(text, url)
    # if 'mtop.taobao.pcdetail.data.ge' in url:
    #     text = await response.text()
    #     print('===>', response.url.split('%22'))
    #     save_to_cache(text, response.url.split('%22')[3])
    #     print('json:', response.url, text)