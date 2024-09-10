import asyncio

import pyppeteer as pt
from pyppeteer.network_manager import Request

from app.ajax_handler import on_response
from app.auth import load_login_data
from app.cache import save_to_cache, load_from_cache
from app.store import Store

# 定义保存的文件路径
cookies_file = 'user_data/cookies.json'
localstorage_file = 'user_data/localstorage.json'
ids = ['692747434364',
       '737538057374',
       '736436305725',
       '820262700721',
       '769269832959',
       '817085314751',
       '734421092543',
       '728560310370',
       '711244172250', ]


# urls = ['https://item.taobao.com/item.htm?id=692747434364']

async def init_page():
    browser = await pt.launch({
        'executablePath': '../chrome-win/chrome.exe',
        'headless': False,
        # 设置Windows-size和Viewport大小来实现网页完整显示
        'args': [
            '--no-sandbox',
            '--window-size=1920,1000',
            '--disable-infobars',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-gpu'
        ],
        'ignoreDefaultArgs': ['--enable-automation'],
    }, devtools=True)
    page = await browser.newPage()
    # 设置浏览器窗口大小
    await page.setViewport(viewport={'width': 1280, 'height': 900})
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


async def fetch_store(store: Store, page):
    page.store = store
    # 打开店铺地址
    await page.goto(store.url)
    # 滚动到店铺底部用于出发商品列表api调用
    # await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    await page.evaluate('''async () => {
      await new Promise((resolve, reject) => {
        var totalHeight = 0;
        var distance = 100;
        var timer = setInterval(() => {
          var scrollHeight = document.body.scrollHeight;
          window.scrollBy(0, distance);
          totalHeight += distance;
          if (totalHeight >= scrollHeight) {
            clearInterval(timer);
            resolve();
          }
        }, 100);
      });
    }''')


async def run():
    page = await init_page()
    # load login data
    await load_login_data(page)

    # 抓取商店
    from store import stores
    for store in stores:
        await fetch_store(store, page)

    # for id in ids:
    #     data = load_from_cache(id)
    #     if data:
    #         print('Load from cache:', id)
    #         continue
    #     await asyncio.sleep(1)
    #     await fetch_product(id, page)

    # await browser.close()
    await asyncio.sleep(10)


if __name__ == '__main__':
    # t = 'https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.6.1&appKey=12574478&t=1725457298896&sign=a30c247bf7c0fe2d35d75407c8db0d62&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&dataType=json&valueType=string&type=json&data=%7B%22id%22%3A%22692747434364%22%2C%22detail_v%22%3A%223.3.2%22%2C%22exParams%22%3A%22%7B%5C%22id%5C%22%3A%5C%22692747434364%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22id%3D692747434364%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fitem.taobao.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%7D%22%7D'
    # print(t.split('%22')[2])
    ev = asyncio.new_event_loop()
    ev.run_until_complete(run())
