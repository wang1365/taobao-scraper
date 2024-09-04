import asyncio
import json
import os

import pyppeteer as pt
from pyppeteer.network_manager import Request

# 定义保存的文件路径
cookies_file = './user_data/cookies.json'
localstorage_file = './user_data/localstorage.json'
ids = ['692747434364']
# urls = ['https://item.taobao.com/item.htm?id=692747434364']

async def save_login_data(page):
    # 保存Cookies
    cookies = await page.cookies()
    with open(cookies_file, 'w') as f:
        json.dump(cookies, f)

    # 保存LocalStorage数据
    local_storage = await page.evaluate('''() => {
        let items = {};
        for (let i = 0; i < localStorage.length; i++) {
            let key = localStorage.key(i);
            items[key] = localStorage.getItem(key);
        }
        return items;
    }''')
    with open(localstorage_file, 'w') as f:
        json.dump(local_storage, f)


async def load_login_data(page):
    # 加载Cookies
    if os.path.exists(cookies_file):
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
            await page.setCookie(*cookies)

    # 加载LocalStorage数据
    # if os.path.exists(localstorage_file):
    #     with open(localstorage_file, 'r') as f:
    #         local_storage = json.load(f)
    #         await page.evaluate('''(items) => {
    #             for (const [key, value] of Object.entries(items)) {
    #                 localStorage.setItem(key, value);
    #             }
    #         }''', local_storage)


def save_to_cache(data, id):
    fp = f'./out/cache/{id}.json'
    print(f'Save to cache:', fp)
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(data)


def load_from_cache(id):
    fp = f'./out/cache/{id}.json'
    if not os.path.exists(fp):
        print(f'Cache not exists:', fp)
        return None

    print(f'Load from cache:', fp)
    with open(fp, 'r', encoding='utf-8') as f:
        return json.load(f)


async def run(need_login=False):
    browser = await  pt.launch({
        'executablePath': './chrome-win/chrome.exe',
        'headless': False,
        # 设置Windows-size和Viewport大小来实现网页完整显示
        'args': [
            '--no-sandbox',
            '--window-size=1824,900',
            '--disable-infobars',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ],
        'ignoreDefaultArgs': ['--enable-automation'],
    }, devtools=True)
    page = await browser.newPage()
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    await page.setExtraHTTPHeaders({
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    })
    cookies = await page.cookies()
    await page.setCookie(*cookies)

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
        if 'mtop.taobao.pcdetail.data.ge' in response.url:
            text = await response.text()
            print('===>', response.url.split('%22'))
            save_to_cache(text, response.url.split('%22')[3])
            print('json:', response.url, text)

    # 启用请求拦截功能
    # await page.setRequestInterception(True)
    # 监听请求事件
    from datetime import datetime
    page.on('request', lambda req: asyncio.ensure_future(handle_request(req)))
    page.on('response', lambda response: asyncio.ensure_future(handle_response(response)))

    if need_login:
        await page.goto('https://login.taobao.com/')
        await asyncio.sleep(60)
        await save_login_data(page)
    else:
        await load_login_data(page)

    for id in ids:
        data = load_from_cache(id)
        if data:
            print('Load from cache:', id)
            continue
        await asyncio.sleep(1)
        await fetch_product(id, page)

    # await browser.close()
    await asyncio.sleep(500)


async def fetch_product(id, page):
    url = f'https://item.taobao.com/item.htm?id={id}'
    await page.goto(url)


if __name__ == '__main__':
    # t = 'https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.6.1&appKey=12574478&t=1725457298896&sign=a30c247bf7c0fe2d35d75407c8db0d62&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&dataType=json&valueType=string&type=json&data=%7B%22id%22%3A%22692747434364%22%2C%22detail_v%22%3A%223.3.2%22%2C%22exParams%22%3A%22%7B%5C%22id%5C%22%3A%5C%22692747434364%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22id%3D692747434364%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fitem.taobao.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%7D%22%7D'
    # print(t.split('%22')[2])
    need_login = False
    ev = asyncio.new_event_loop()
    ev.run_until_complete(run(need_login))
