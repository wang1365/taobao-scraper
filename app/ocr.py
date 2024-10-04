import hashlib
import os

import pytesseract
from PIL import Image
import requests
import threading

image_dir = './out/images'


def get_image_from_url(url) -> str:
    key = hashlib.md5(url.encode()).hexdigest()
    image_path = f'{image_dir}/{key}.jpg'
    if os.path.exists(image_path):
        return image_path

    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
    })
    # 检查请求是否成功
    if response.status_code == 200:
        # 打开一个文件用于写入，并设置为二进制写模式
        # if not os.path.exists(image_path):
        #     os.makedirs(image_dir, exist_ok=True)
        with open(image_path, 'wb') as f:
            # 写入获取到的数据
            f.write(response.content)
        print(f"图片已下载并保存到 {image_path}")
    else:
        print("图片下载失败", response.status_code, response.text)
    return image_path


def to_text_task(url: list[str], result) -> list[str]:
    try:
        fp = get_image_from_url(url)
        # 打开图像文件
        image = Image.open(fp)
    except Exception as e:
        print(e)
        return
    if not fp:
        return

    # 进行文字识别
    text = pytesseract.image_to_string(image, lang='chi_sim')
    text = text.strip()

    # 打印识别结果
    print(text)
    if text:
        result.append(text)


def to_text(images: list[str]) -> list[str]:
    result = []
    threads = [threading.Thread(target=to_text_task, args=(image, result)) for image in images]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print('====>result', result)
    return result
