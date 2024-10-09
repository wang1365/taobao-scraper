import hashlib
import os

import pytesseract
from PIL import Image
import requests
import threading

image_dir = './out/images'


def save_lost_images(url):
    with open('./out/lost_images/data.txt', 'a') as f:
        f.write(url + '\n')


def read_lost_images():
    with open('./out/lost_images/data.txt') as f:
        s = f.readlines()
        print(s)
        return [t.strip('\n') for t in s]


lost_images = read_lost_images()


def get_image_from_url(product_id, url) -> str:
    if url in lost_images:
        return ''
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
        print(f"{product_id} 图片已下载并保存到 {image_path}")
    else:
        print(f"{product_id} 图片下载失败", url, response.status_code, response.text)
        save_lost_images(url)
    return image_path


def to_text_task(product_id, i, url, result):
    try:
        fp = get_image_from_url(product_id, url)
        # 打开图像文件
        image = Image.open(fp)
    except Exception as e:
        print(e)
        return
    if not fp:
        return

    # 进行文字识别
    # text = pytesseract.image_to_string(image, lang='chi_sim+eng')
    text = pytesseract.image_to_string(image, lang='chi_sim')
    text = text.strip()

    # 打印识别结果
    print(text)
    if text:
        text = text.replace('\\n\\n', '\\n')
        text = text.replace('\\n', '\n')
        result.append((i, text))


def to_text(product_id, images: list[str]) -> list[str]:
    result = []
    # 并发进行ocr识别提取文本，为了保持顺序，需要把图片index传入
    threads = [threading.Thread(target=to_text_task, args=(product_id, i, image, result)) for i, image in
               enumerate(images)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print('====>result', result)
    result.sort(key=lambda x: x[0])
    return [txt for i, txt in result]
