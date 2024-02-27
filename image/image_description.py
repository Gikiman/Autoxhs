import base64  
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel

def convert_to_base64(image_file):   
    encoded_string = base64.b64encode(image_file.read()).decode()  
    return encoded_string  

def get_image_description(image_files,openai_api_key):
    image_message = {
            "type": "image_url",
            "image_url": {
                "url": "data:image/png;base64,{base64image}"
            }
        }
    text_message = {"type": "text", "text": "请对图片的内容进行简洁描述，包括但不限于场景、情感、颜色、活动等."}
    messages = [text_message, image_message]
    descripton_prompt = ChatPromptTemplate.from_messages([
        ("user", messages)
    ])
    llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    model="gpt-4-vision-preview",
    max_tokens=300)
    chain = descripton_prompt | llm
    descriptor = RunnableParallel(basic = chain)
    
    images =[]
    for image_file in image_files:
        images.append({"base64image":convert_to_base64(image_file)})
    responses = descriptor.batch(images)
    
    descriptions = {}
    for index,response in enumerate(responses, start=1):
        descriptions[index] = response['basic']['content']
    return descriptions
