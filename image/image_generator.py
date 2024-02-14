import requests
import os 
def get_image_openai(client,images_model,prompt,path):

    path = os.path.join(path,'dalle3.png')
    
    response = client.images.generate(
        model=images_model,
        prompt=prompt,
        n=1,
        size="1024x1024"
        )
    image_url = response.data[0].url

    # 发送 HTTP 请求并获取响应
    response = requests.get(image_url)

    # 确保请求成功
    if response.status_code == 200:
        # 替换为你想保存的文件路径
        with open(path, 'wb') as file:
            file.write(response.content)
        print("图片内容生成成功")
        return path
    else:
        print("下载失败，状态码：", response.status_code)