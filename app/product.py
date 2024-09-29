import os
from urllib.parse import urlparse, parse_qs

# base_dir = './out/data/items'
base_dir = './out/data_0926'
base_items_dir = './out/data_0926/items'
lost_file = f'{base_dir}/lost.txt'

# if os.path.exists(lost_file):
#     os.(lost_file, exist_ok=True)


def exist(product_id):
    return os.path.exists(f'{base_items_dir}/{product_id}.json')


def save(product_id, data):
    with open(f'{base_dir}/{base_items_dir}.json', 'w', encoding='utf-8') as f:
        f.write(data)


def save_desc(product_id, data):
    with open(f'{base_dir}/{base_items_dir}_desc.json', 'w', encoding='utf-8') as f:
        f.write(data)


def parse_id(url):
    ret = urlparse(url)
    return parse_qs(ret.query)['id'][0]


def check_exists(product_id):
    if not os.path.exists(lost_file):
        return True
    with open(lost_file) as f:
        items = [s.strip() for s in f.readlines()]
        return product_id not in items


def set_not_exists(product_id):
    with open(lost_file, 'a') as f:
        f.write(f'{product_id}\n')


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
