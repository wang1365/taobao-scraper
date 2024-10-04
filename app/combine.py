import json
import os.path
import re

from openpyxl import Workbook
from pathlib import Path
from openpyxl.styles import Font
import itertools
import product
import ocr


def dumps(s):
    if not s:
        return ''
    return json.dumps(s, ensure_ascii=False)


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
               'Product Params', 'Images', 'Videos', 'Description Images',
               'Image Text']
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
    ws.column_dimensions[_()].width = 100  # Video
    ws.column_dimensions[_()].width = 150  # Detail Images

    ws.column_dimensions[_()].width = 150  # Detail Images

    return wb


def get_detail_images(product_id):
    file = f'{product.base_items_dir}/{product_id}_desc.json'
    if not os.path.exists(file):
        return ''
    result = set()
    print('Start parse desc images for:', product_id)
    with open(file, encoding='utf8') as f:
        f_str = f.read()
        if not f_str.startswith('{'):
            f_str = f_str[2:]
        data = json.loads(f_str)

        if 'components' in data['data']:
            componentData = data['data']['components']['componentData']
            if 'desc_richtext_pc' in componentData:
                text = componentData['desc_richtext_pc']['model']['text']
                url_pattern1 = r'background="(https?://[^"]+)"'
                url_pattern2 = r'src="(https://img.[^"]+)"'
                urls1 = re.findall(url_pattern1, text)
                urls2 = re.findall(url_pattern2, text)

                """
                src=\"https://img.alicdn.com/imgextra/i4/432776619/O1CN01MmGgvq1ylYKTrKA1c_!!432776619.jpg\"
                """

                for url in urls1:
                    result.add(url)
                for url in urls2:
                    result.add(url)

            for k, v in componentData.items():
                print('========>kv', k, v)
                if 'detail_pic_' not in k:
                    continue
                pic = v['model'].get('picUrl') or ''
                if not pic.startswith('http'):
                    pic = f'https:{pic}'
                if pic:
                    result.add(pic)

        if 'wdescContent' in data['data']:
            for page in data['data']['wdescContent']['pages']:
                url = page.split('>')[1].split('<')[0]
                result.add(url)

    print('>>>>>> desc images:', product_id, result)
    return list(result)


def get_inventory(data):
    """
    "skus": [{
                    "propPath": "1627207:628420314;20509:28314", // "pid_a: vid_a1; pid_b: vid_b1"
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
         sku: {
            pid:vid,
            pid2:vid
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
    # vid对应的图片
    vid_images = {}
    for pid in props_json:
        props[pid['pid']] = pid['name']
        for value in pid['values']:
            props[value['vid']] = value['name']
            vid_images[value['vid']] = value.get('image')

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
    inventory_detail = []
    for sku_id, detail in inventory_info.items():
        vids = sku_map.get(sku_id)
        if not vids:
            continue
        prop_names = [props.get(v) for v in vids]
        sku_images = list(filter(lambda x: x is not None, [vid_images.get(vid) for vid in vids]))
        quantity = detail['quantity']
        inventory_detail.append({
            'options': prop_names,
            'image_url': sku_images[0] if sku_images else '',
            'quantity': int(quantity)
        })
    return inventory_total, sorted(inventory_detail, key=lambda x: x['options'])


def run():
    wb = init_excel()

    products = []
    i = 0
    for json_file in Path('./out/data').rglob('*.json'):
        i += 1
        print(f'[{i}]=====> start parse: {json_file}')
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

            # description images
            detail_images = get_detail_images(item_id)

            # Image text
            image_text = ocr.to_text(detail_images)

            products.append([shopId, shopName, origin_price, extra_price,
                             item_id, title, product_link,
                             inventory_total, dumps(inventory_detail), dumps(sku), dumps(sku_image),
                             seller_id, sellerNick,
                             dumps(params), dumps(images), dumps(videos), dumps(detail_images),
                             dumps(image_text)
                             ])

    # 按照shop id排序
    products.sort(key=lambda x: x[0])
    for product in products:
        wb.active.append(product)

    wb.save('./out/result/taobao.xlsx')


if __name__ == '__main__':
    run()
