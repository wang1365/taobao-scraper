import asyncio
import json
import os

import pyppeteer as pt

# 定义保存的文件路径
cookies_file = 'user_data/cookies.json'
localstorage_file = 'user_data/localstorage.json'


async def save_login_data(page):
    """
    Save cookies and LocalStorage data
    :param page:
    :return:
    """
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
    """
    Load cookies and LocalStorage data
    :param page:
    :return:
    """
    # 加载Cookies
    if os.path.exists(cookies_file):
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
            await page.setCookie(*cookies)


async def login():
    """
    Login to Taobao, need to manually enter the verification code
    :return:
    """
    browser = await  pt.launch({
        'executablePath': '../chrome-win/chrome.exe',
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

    await page.goto('https://login.taobao.com/')
    await asyncio.sleep(60)
    await save_login_data(page)
    await browser.close()


if __name__ == '__main__':
    ev = asyncio.new_event_loop()
    ev.run_until_complete(login())
