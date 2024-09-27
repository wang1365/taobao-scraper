import asyncio
import json
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import pyppeteer as pt
from pyppeteer.network_manager import Request

import product
from app.ajax_handler import on_response
from app.auth import load_login_data
from app.dingtalk import send_dingtalk


# urls = ['https://item.taobao.com/item.htm?id=692747434364']

# 爬虫检测 https://bot.sannysoft.com/

def on_response(url, text):
    print(f'{datetime.now()} Response: {url} Status: {text}')

    # 商品详情API
    if 'mtop.taobao.pcdetail.data.get' in url:
        parsed_url = urlparse(url)
        qs = parse_qs(parsed_url.query)
        data = json.loads(text)
        product_id = data['data']['item']['itemId']
        product.save(product_id, text)

    # 商品详情 - 描述API
    if 'mtop.taobao.detail.getdesc' in url:
        parsed_url = urlparse(url)
        qs = parse_qs(parsed_url.query)
        product_id = json.loads(qs['data'][0])['id']

        text = text.lstrip(' mtopjsonp2(').rstrip(')')
        product.save_desc(product_id, text)


async def init_page():
    browser = await pt.launch({
        'executablePath': '../chrome-win/chrome.exe',
        'headless': False,
        # 设置Windows-size和Viewport大小来实现网页完整显示
        'args': [
            '--no-sandbox',
            '--window-size=1720,900',
            '--disable-infobars',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            # '--disable-gpu'
        ],
        'ignoreDefaultArgs': ['--enable-automation'],
    }, devtools=False)
    page = await browser.newPage()
    # 设置浏览器窗口大小
    await page.setViewport(viewport={'width': 1720, 'height': 900})
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    await page.setExtraHTTPHeaders({
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    })

    await page.evaluate('''() => {
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                Object.defineProperty(navigator, 'userAgent', { get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' });
            }''')

    # 定义监听器，拦截并处理请求
    async def handle_request(req: Request):
        await req.continue_()

    async def handle_response(response):
        # print(f'{datetime.now()} Response: {response.url} Status: {response.text()}')
        if 'h5api' in response.url:
            text = await response.text()
            on_response(response.url, text)

    # 启用请求拦截功能
    # await page.setRequestInterception(True)
    # 监听请求事件
    page.on('request', lambda req: asyncio.ensure_future(handle_request(req)))
    page.on('response', lambda response: asyncio.ensure_future(handle_response(response)))
    return page


async def run():
    page = await init_page()
    # load login data
    await load_login_data(page)

    with open('./out/data/products.txt', 'r', encoding='utf-8') as f:
        product_urls = f.readlines()

    # 遍历商品进行抓取
    for i, url in enumerate(product_urls):
        print(f'=======================> [{i + 1}/{len(product_urls)}] Start load product detail page:', url)
        product_id = product.parse_id(url)
        if product.exist(product_id):
            print('Load from cache:', product_id)
            continue

        # 跳转到商品详情页
        print('Start load product detail page:', product_id)
        await page.goto(url)
        await page.evaluate('''() => { Object.defineProperties(navigator, {webdriver: { get: () => false }}) }''')

        # 等待页面加载完成，
        await asyncio.sleep(random.randint(5, 10))
        if not page.url.startswith('https://item.taobao.com'):
            # 如果页面跳转了，说明可能触发了机制，需要通知人工介入
            send_dingtalk(f'Error: {product_id} prevented')

        await page.evaluate('''async () => {
              await new Promise((resolve, reject) => {
                var totalHeight = 0;
                var distance = 100;
                var timer = setInterval(() => {
                  var scrollHeight = 2000;
                  window.scrollBy(0, distance);
                  totalHeight += distance;
                  if (totalHeight >= scrollHeight) {
                    clearInterval(timer);
                    resolve();
                  }
                }, 100);
              });
            }''')
        await asyncio.sleep(random.randint(10, 30))
    # await browser.close()
    await asyncio.sleep(500)


if __name__ == '__main__':
    # t = 'https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.6.1&appKey=12574478&t=1725457298896&sign=a30c247bf7c0fe2d35d75407c8db0d62&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&dataType=json&valueType=string&type=json&data=%7B%22id%22%3A%22692747434364%22%2C%22detail_v%22%3A%223.3.2%22%2C%22exParams%22%3A%22%7B%5C%22id%5C%22%3A%5C%22692747434364%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22id%3D692747434364%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fitem.taobao.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%7D%22%7D'
    # print(t.split('%22')[2])
    ev = asyncio.new_event_loop()
    ev.run_until_complete(run())
