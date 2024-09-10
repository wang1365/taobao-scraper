import hashlib
import json
import os

import requests


def save_to_cache(data, user_key):
    # 使用md5对key进行编码
    # key = hashlib.md5(user_key.encode()).hexdigest()
    key = user_key

    fp = f'./out/cache/{key}.json'
    print(f'Save to cache:', user_key, key, fp)
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(data)

    image_dir = f'./out/cache/{key}_images'
    json_data = json.loads(data)
    images = json_data['data']['item']['images']
    for i, img in enumerate(images):
        print(f'Save image:', img)
        response = requests.get(img, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
        })
        # 检查请求是否成功
        if response.status_code == 200:
            # 打开一个文件用于写入，并设置为二进制写模式
            image_path = f'{image_dir}/{key}-{i + 1}.jpg'
            if not os.path.exists(image_path):
                os.makedirs(image_dir, exist_ok=True)
            with open(image_path, 'wb') as f:
                # 写入获取到的数据
                f.write(response.content)
            print(f"图片已下载并保存到 {image_path}")
        else:
            print("图片下载失败")


def load_from_cache(user_key):
    # 使用md5对key进行编码
    # key = hashlib.md5(user_key.encode()).hexdigest()
    key = user_key

    fp = f'./out/cache/{key}.json'
    if not os.path.exists(fp):
        print(f'Cache not exists:', fp)
        return None

    print(f'Load from cache:', fp)
    with open(fp, 'r', encoding='utf-8') as f:
        return json.load(f)
