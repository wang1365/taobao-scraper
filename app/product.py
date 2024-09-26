import os
from urllib.parse import urlparse, parse_qs


# base_dir = './out/data/items'
base_dir = './out/data_0926/items'

def exist(product_id):
    return os.path.exists(f'{base_dir}/{product_id}.json')


def save(product_id, data):
    with open(f'{base_dir}/{product_id}.json', 'w', encoding='utf-8') as f:
        f.write(data)


def save_desc(product_id, data):
    with open(f'{base_dir}/{product_id}_desc.json', 'w', encoding='utf-8') as f:
        f.write(data)


def parse_id(url):
    ret = urlparse(url)
    return parse_qs(ret.query)['id'][0]


class ProductDetailPage:
    """
    https://item.taobao.com/item.htm?id=688023352283
    """

    def __init__(self, url):
        self.url = url
        ret = urlparse(url)
        self.id = parse_qs(ret.query)['id']

    def __str__(self):
        return self.url

    def __repr__(self):
        return self.url
