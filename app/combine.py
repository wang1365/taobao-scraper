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
               'Inventory Total', 'Inventory Detail',
               'SKU', 'Sku Picture',
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

    ws.column_dimensions[_()].width = 15  # INVENTORY TOTAL
    ws.column_dimensions[_()].width = 25  # INVENTORY DETAIL
    ws.column_dimensions[_()].width = 25  # sku
    ws.column_dimensions[_()].width = 25  # sku picture

    ws.column_dimensions[_()].width = 12  # SELLER ID
    ws.column_dimensions[_()].width = 15  # SELLER NAME

    ws.column_dimensions[_()].width = 150  # PRODUCT PARAMS
    ws.column_dimensions[_()].width = 150  # IMAGES
    ws.column_dimensions[_()].width = 150  # Video

    return wb


def get_inventory(data):
    """
    "skus": [{
                    "propPath": "1627207:628420314;20509:28314",
                    "skuId": "4908138313350"
                }]
    :param data:
    :return:
    """
    skus = data['skuBase']['skus']
    '''
    { 
         "4908138313350": {
             "1627207": "628420314",
             "20509": "28314",
         } 
     }
    '''
    sku_map = {k['skuId']: k['propPath'] for k in skus}
    for k, v in sku_map.items():
        sku = v
        sku = sku.split(';')
        sku_map[k] = [_.split(':')[1] for _ in sku]

    '''
    "props": [{
                    "comboProperty": "false",
                    "hasImage": "true",
                    "name": "颜色分类",
                    "nameDesc": "（4）",
                    "pid": "1627207",
                    "values": [{
                            "comboPropertyValue": "false",
                            "image": "https://gw.alicdn.com/bao/uploaded/i3/2212252545501/O1CN01FYU7Lq1qVVXr7dAcX_!!2212252545501.jpg",
                            "name": "锡器灰 现货",
                            "sortOrder": "7",
                            "vid": "628420314"
                        }
    '''
    if 'props' not in data['skuBase']:
        return data['skuCore']['sku2info']['0']['quantity'] + data['skuCore']['sku2info']['0']['quantityText'], ''
    props_json = data['skuBase']['props']
    props = {}
    for pid in props_json:
        props[pid['pid']] = pid['name']
        for value in pid['values']:
            props[value['vid']] = value['name']

    '''
    "skuCore": {
            "sku2info": {
                "0": {
                    "logisticsTime": "48小时内发货，预计明天送达",
                    "moreQuantity": "false",
                    "price": {
                        "priceMoney": "179820",
                        "priceText": "1798.2"
                    },
                    "quantity": "17",
                    "quantityDisplayValue": "1",
                    "quantityText": "有货",
                    "subPrice": {
                        "priceBgColor": "#FF5000",
                        "priceColor": "#FFFFFF",
                        "priceMoney": "159520",
                        "priceText": "1595.2",
                        "priceTitle": "券后",
                        "priceTitleColor": "#FFFFFF"
                    }
                },
                "4908138313351": {
    '''
    inventory_info = data['skuCore']['sku2info']

    inventory_total = inventory_info['0']['quantity'] + ' ' + inventory_info['0']['quantityText']
    inventory_detail = ''
    for sku_id, detail in inventory_info.items():
        properties = sku_map.get(sku_id)
        if not properties:
            continue
        prop_names = ' '.join([props.get(v) for v in properties])
        inventory_detail += f'{prop_names} {detail["quantity"]} {detail["quantityText"]} | '
    return inventory_total, inventory_detail.strip(' | ')


if __name__ == '__main__':
    wb = init_excel()

    products = []
    for json_file in Path('./out/data').rglob('*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)['data']
            item_id = data['item']['itemId']
            product_link = f'https://item.taobao.com/item.htm?id={item_id}'

            # 商品价格
            priceVo = data['componentsVO']['priceVO']
            origin_price = data['componentsVO']['priceVO']['price']['priceText']
            if 'extraPrice' in data['componentsVO']['priceVO']:
                extra_price = priceVo['extraPrice']['priceText']
            else:
                extra_price = ''

            # 商品名称
            title = data['item']['title']

            # 商品图片
            images = data['item']['images']
            # 商品视频 以及商品视频缩略图
            if 'videos' in data['item']:
                videos = []
                for video in data['item']['videos']:
                    images.append(video['videoThumbnailURL'])
                    videos.append(video['url'])
            else:
                videos = ''
            # 商品库存
            inventory_total, inventory_detail = get_inventory(data)

            # 商家信息
            seller_id = data['seller']['sellerId']
            sellerNick = data['seller']['sellerNick']

            # 店铺信息
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

                sku_image = {}
                for t in data['skuBase']['props']:
                    for v in t['values']:
                        if 'image' in v:
                            sku_image[v['name']] = v['image']
            else:
                print('No sku, skip', item_id, data)
                continue

            products.append([shopId, shopName, origin_price, extra_price,
                             item_id, title, product_link,
                             inventory_total, inventory_detail, str(sku), str(sku_image),
                             seller_id, sellerNick,
                             str(params), str(images), str(videos)])

    # 按照shop id排序
    products.sort(key=lambda x: x[0])
    for product in products:
        wb.active.append(product)

    wb.save('./out/result/taobao.xlsx')
