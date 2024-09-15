import json

from openpyxl import Workbook
from pathlib import Path
from openpyxl.styles import Font
import itertools


def init_excel():
    # 创建一个新的工作簿
    wb = Workbook()
    # 选择默认的工作表
    ws = wb.active
    # 给工作表命名
    ws.title = "taobao"

    columns = ['Shop Id', 'Shop Name', 'Origin Price', 'Extra Price',
               'Product Id', 'Product Name', 'Product Link',
               'SKU',
               'Seller ID', 'Seller Name',
               'Product Params', 'Images', 'Videos']
    ws.append(columns)

    # 冻结首行
    ws.freeze_panes = "A2"

    # 创建字体对象
    font = Font(bold=True, color="FF0000", size=11, name='Arial')

    # 应用字体样式到单元格
    for i in range(len(columns)):
        ws.cell(1, i + 1).font = font

    counter = itertools.count(start=0, step=1)
    _ = lambda: chr(ord('A') + next(counter))
    ws.column_dimensions[_()].width = 12  # SHOP ID
    ws.column_dimensions[_()].width = 20  # SHOP NAME
    ws.column_dimensions[_()].width = 11  # ORIGIN PRICE
    ws.column_dimensions[_()].width = 11  # extra price

    ws.column_dimensions[_()].width = 15  # PRODUCT ID
    ws.column_dimensions[_()].width = 60  # PRODUCT NAME
    ws.column_dimensions[_()].width = 50  # PRODUCT NAME

    ws.column_dimensions[_()].width = 50  # sku

    ws.column_dimensions[_()].width = 12  # SELLER ID
    ws.column_dimensions[_()].width = 15  # SELLER NAME

    ws.column_dimensions[_()].width = 150  # PRODUCT PARAMS
    ws.column_dimensions[_()].width = 150  # IMAGES
    ws.column_dimensions[_()].width = 150  # Video

    return wb


if __name__ == '__main__':
    wb = init_excel()

    products = []
    for json_file in Path('./out/data').rglob('*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)['data']
            item_id = data['item']['itemId']
            product_link = f'https://item.taobao.com/item.htm?id={item_id}'

            priceVo = data['componentsVO']['priceVO']
            origin_price = data['componentsVO']['priceVO']['price']['priceText']
            if 'extraPrice' in data['componentsVO']['priceVO']:
                extra_price = priceVo['extraPrice']['priceText']
            else:
                extra_price = ''
            title = data['item']['title']
            images = data['item']['images']
            if 'videos' in data['item']:
                videos = []
                for video in data['item']['videos']:
                    images.append(video['videoThumbnailURL'])
                    videos.append(video['url'])
            else:
                videos = ''

            seller_id = data['seller']['sellerId']
            sellerNick = data['seller']['sellerNick']
            shopId = data['seller']['shopId']
            shopName = data['seller']['shopName']

            infos = list(
                filter(lambda info: info['type'] == 'BASE_PROPS', data['componentsVO']['extensionInfoVO']['infos']))
            params = infos[0]['items'] if len(infos) > 0 else ''

            if 'props' in data['skuBase']:
                sku = [{
                    'name': t['name'],
                    'values': [_['name'] for _ in t['values']]
                }
                    for t in data['skuBase']['props']]

                products.append([shopId, shopName, origin_price, extra_price,
                                 item_id, title, product_link,
                                 str(sku),
                                 seller_id, sellerNick,
                                 str(params), str(images), str(videos)])
            else:
                sku = ''

    # 按照shop id排序
    products.sort(key=lambda x: x[0])
    for product in products:
        wb.active.append(product)

    wb.save('./out/result/taobao.xlsx')
