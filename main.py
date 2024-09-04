import asyncio
from time import sleep

import pyppeteer as pt

urls = ['https://item.taobao.com/item.htm?id=692747434364']


async def run():
    browser = await  pt.launch({
        'executablePath': './chrome-win/chrome.exe',
        'headless': False,
        # 设置Windows-size和Viewport大小来实现网页完整显示
        'args': ['--no-sandbox', '--window-size=1024,600', '--disable-infobars']
    }, devtools=True)
    page = await browser.newPage()


    # await page.evaluateOnNewDocument('''()=>{ Object.defineProperties(navigator,{ 'webdriver':{ get: ()=> false } }) }''')
    # await page.evaluateOnNewDocument('''()=>{ Object.defineProperties(navigator,{ 'languages':{ get: ()=> ['en-us', 'en'] } })}''')
    # await page.evaluateOnNewDocument('''() => {Object.defineProperties(navigator, {'plugins': {get: () => [1, 2, 3, 4, 5]}})}''')
    # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    # await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
    # await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    # 定义监听器，拦截并处理请求
    async def handle_request(req):
        print('==>', req.resourceType, req.url)
        await req.continue_()

    async def handle_response(response):
        # print(response.text())
        pass
    # 启用请求拦截功能
    await page.setRequestInterception(True)
    # 监听网络响应
    # await page.evaluateOnNewDocument("""
    #    () => {
    #        window._networkIntercept = [];
    #        window._originalFetch = window.fetch;
    #        window.fetch = (resource, init) => {
    #            window._networkIntercept.push({ resource, init });
    #            return window._originalFetch(resource, init);
    #        };
    #    }
    #    """)
    # 监听请求事件
    # page.on('request', lambda req: asyncio.ensure_future(handle_request(req)))
    # page.on('response', lambda res: asyncio.ensure_future(handle_response(res)))
    await page.goto(urls[0])

    # await browser.close()
    await asyncio.sleep(500)
    sleep(10000)


if __name__ == '__main__':
    from pyppeteer import chromium_downloader

    print('1', pt.__chromium_revision__)
    print('2', pt.chromium_downloader.chromiumExecutable.get('win64'))
    print('3', pt.chromium_downloader.downloadURLs.get('win64'))
    # 在这里使用的是淘宝镜像中的chromium
    # 进入这个网址
    # https://developer.aliyun.com/mirror/
    # https://npm.taobao.org/mirrors/chromium-browser-snapshots
    # 选择对应系统和对应的版本（我这里是mac系统，选择了我系统默认的588429）

    ev = asyncio.get_event_loop()
    ev.run_until_complete(run())
