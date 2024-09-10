import os.path

_stores = [
    'https://shop511077228.taobao.com/?spm=pc_detail.29232929/evo401271b517998.shop_block.dshopinfo.4cb17dd6Y3LKnA',
    'https://shop110961927.taobao.com/?spm=pc_detail.29232929/evo401271b517998.shop_block.dshopinfo.ff4d7dd6ITwzR8',
    'https://shop104259596.taobao.com/?spm=pc_detail.29232929/evo401271b517998.shop_block.dshopinfo.442c7dd6pyvA7e',

    # 'https://itoshiroshi.taobao.com/search.htm?spm=a1z10.1-c-s.0.0.65387f9c90qoJn&search=y',
    # 'https://ac2012.taobao.com/search.htm?spm=a1z10.1-c.0.0.1faf5fe3kvUuk3&search=y',

    'https://shop115569367.taobao.com/?spm=pc_detail.29232929/evo401271b517998.shop_block.dshopinfo.69737dd6cuvR4f',
    'https://shop102738814.taobao.com/?spm=pc_detail.29232929/evo401271b517998.shop_block.dshopinfo.fe877dd6MbF2db',
    'https://shop156488437.taobao.com/?spm=pc_detail.29232929/evo401271b517998.shop_block.dshopinfo.fcd37dd6G0dB6C',
    'https://shop128548716.taobao.com/?spm=pc_detail.29232929/evo401271b517998.shop_block.dshopinfo.15b77dd6dt8cD1',
    'https://shop367593833.taobao.com/search.htm?spm=a1z10.1-c.0.0.4c0d5d0ca2vgg1&search=y',
    'https://shop57101119.taobao.com/?spm=pc_detail.29232929/evo401271b517998.shop_block.dshopinfo.add57dd6RwdtPJ',
    # 'https://monika88.taobao.com/search.htm?spm=a1z10.1-c-s.w5002-14513604863.4.3ca94a97wMTqQK&search=y&orderType=hotsell_desc&scene=taobao_shop',
    'https://shop538769016.taobao.com/?spm=pc_detail.29232929/evo401271b517998.shop_block.dshopinfo.63c47dd6g7W9ep',

]


class Store(object):
    """
    Store
    店铺商品列表API:
        https://h5api.m.taobao.com/h5/mtop.taobao.shop.simple.fetch/1.0/
        https://h5api.m.taobao.com/h5/mtop.taobao.shop.simple.item.fetch/1.0/
    """

    def __init__(self, url):
        self.url = url
        self.id = url.split('.taobao.com')[0].split('//')[1]
        self.path = f'./out/cache/{self.id}'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def __str__(self):
        return f'<Store {self.id}>'

    def __repr__(self):
        return self.__str__()


stores = [Store(url) for url in _stores]
