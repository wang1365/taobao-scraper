import wechatsogou

def run():
    # 直连
    ws_api = wechatsogou.WechatSogouAPI()

    # 验证码输入错误的重试次数，默认为1
    ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)

    # 所有requests库的参数都能在这用
    # 如 配置代理，代理列表中至少需包含1个 HTTPS 协议的代理, 并确保代理可用
    # ws_api = wechatsogou.WechatSogouAPI(proxies={
    #     "http": "127.0.0.1:8888",
    #     "https": "127.0.0.1:8888",
    # })

    # 如 设置超时
    ws_api = wechatsogou.WechatSogouAPI(timeout=0.1)
    result = ws_api.get_gzh_info('南航青年志愿者')
    print(result)

if __name__ == '__main__':
    run()