import requests
import os 
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_openai import OpenAI
def get_image_openai(client,image_model,prompt,path):

    path = os.path.join(path,'dalle3.png')
    
    response = client.images.generate(
        model=image_model,
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

def get_image_langchain(client,prompt,path):

    path = os.path.join(path,'dalle3.png')
    
    image_url = client.get_image(prompt)

    # 发送 HTTP 请求并获取响应
    response = requests.get(image_url)

    # 确保请求成功
    if response.status_code == 200:
        # 替换为你想保存的文件路径
        with open(path, 'wb') as file:
            file.write(response.content)
        return path
    else:
        print("下载失败，状态码：", response.status_code)