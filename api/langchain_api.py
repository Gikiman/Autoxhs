from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder,PromptTemplate
from langchain.schema import SystemMessage
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain.chains.router.llm_router import LLMRouterChain,RouterOutputParser
from langchain_core.runnables import RunnableParallel
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from config.category import categoryInfos
from utils import convert_to_base64
import json
import asyncio
class LangChainClient:
    def __init__(self, api_key,image_model = "dall-e-3" ,text_model="gpt-4-0125-preview", tools=None):
        self.api_key = api_key
        self.image_model = image_model
        self.text_model = text_model
        
        self.tools = tools

        # Initialize the Conversation Buffer Memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Initialize the output parser
        self.parser = JsonOutputToolsParser()

    def get_text(self, system_prompt,human_input,tool_choice):
        
        self.process_memory()
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}")
        ])

        llm = ChatOpenAI(model=self.text_model,api_key = self.api_key).bind(tools=self.tools, tool_choice=tool_choice)
        # Initialize the LLM Chain
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,
            memory=self.memory,
            output_parser=self.parser
        )
        response = llm_chain.invoke(human_input)
        return response
        
    def get_image(self,prompt):
        
        image_url = DallEAPIWrapper(model= self.image_model,api_key = self.api_key).run(prompt)
   
        return image_url
    
    def process_memory(self):   
        if len(self.memory.chat_memory.messages) !=0 and type(self.memory.chat_memory.messages[-1].content) !=str:
            self.memory.chat_memory.messages[-1].content = json.dumps(self.memory.chat_memory.messages[-1].content[0]['args'],ensure_ascii=False)
        
    def cleam_memory(self,idx): #idx剩余多少条  
        self.memory.chat_memory.messages = self.memory.chat_memory.messages[:idx]
        
def autoCategorize(human_input,text_model,api_key):
        
    prompt_infos = categoryInfos
    
    llm = ChatOpenAI(model=text_model,api_key = api_key)
    
    destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
    destinations_str = "\n".join(destinations)
    router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
        destinations=destinations_str
    )
    
    router_prompt = PromptTemplate(
        template=router_template,
        input_variables=["input"],
        output_parser=RouterOutputParser(),
    )
    router_chain = LLMRouterChain.from_llm(llm, router_prompt,verbose = True)

    response = router_chain.invoke(human_input)
    
    return response['destination']

def autoImageCategorize(image_description,text_model,api_key):
    
    llm = ChatOpenAI(model=text_model,openai_api_key=api_key)   
    # 1.先根据图片描述得到一个简化的故事概要 
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content="结合用户提供的一系列图片描述，创作一个连贯的故事概要，不超过100字。"
            ),  # The persistent system prompt
            HumanMessagePromptTemplate.from_template(
                "{human_input}"
            ),  # Where the human input will injected
        ]
    )


    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True
    )
    response = llm_chain.invoke("多张图片描述：{}".format(image_description))
    dump_abstraction = response['text']
    
    # 2.根据故事概要选择贴文类型
    prompt_infos = categoryInfos
    
    llm = ChatOpenAI(model=text_model,api_key = api_key)
    
    destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
    destinations_str = "\n".join(destinations)
    router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
        destinations=destinations_str
    )
    
    router_prompt = PromptTemplate(
        template=router_template,
        input_variables=["input"],
        output_parser=RouterOutputParser(),
    )
    router_chain = LLMRouterChain.from_llm(llm, router_prompt,verbose = True)

    response = router_chain.invoke(dump_abstraction)
    
    return response['destination']

async def my_function(descriptor,images):
    return await descriptor.abatch(images)

def get_image_description(image_files,api_key,vision_model ="gpt-4-vision-preview"):

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
    openai_api_key=api_key,
    model=vision_model,
    max_tokens=300)

    descriptor = LLMChain(
        llm=llm,
        prompt=descripton_prompt,
    )
    images =[]
    for image_file in image_files:
        images.append({"base64image":convert_to_base64(image_file)})
    responses =  asyncio.run(my_function(descriptor, images))
    
    descriptions = ""
    for index,response in enumerate(responses, start=1):
        if index == len(responses):
            descriptions += f"{str(index)}. {str(response['text'])} "
        else:
            descriptions += f"{str(index)}. {str(response['text'])} \n"

    return descriptions