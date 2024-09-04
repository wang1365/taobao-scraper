import  requests

id=123
image_dir = f'./out/cache/{id}_images'
img = 'https://img.alicdn.com/imgextra/i3/689266012/O1CN01TG2qmw1uHY2FBBBv5_!!689266012.jpg'
response = requests.get(img, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
})
id=123
# 检查请求是否成功
if response.status_code == 200:
    # 打开一个文件用于写入，并设置为二进制写模式
    image_path = f'./out/{id}.jpg'
    with open(image_path, 'wb') as f:
        # 写入获取到的数据
        f.write(response.content)
    print(f"图片已下载并保存到 {image_path}")
else:
    print("图片下载失败", response.status_code, response.text)