import json
from utils import remove_hash_and_asterisk

def get_topics(xhs_client,tags):
    topics = []

    tag_list = tags.split("#")
    
    if '' in tag_list:
        tag_list.remove('')

    for tag in tag_list:
        tag_info_list = xhs_client.get_suggest_topic(tag)
        if len(tag_info_list)!=0:
            tag_info = tag_info_list[0]
            topics.append({"id": tag_info["id"], "name": tag_info["name"], 
                           "type": "topic", "link":tag_info["link"]})
        else:
            print("Couldn't found",tag)
    return topics

def get_topics_suffix(topics):
    topics_suffix = []
    for topic in topics:
        name = topic["name"]
        topics_suffix.append("#{}[话题]#".format(name))
    topics_suffix = " ".join(topics_suffix)
    topics_suffix = "\n "+topics_suffix

    return topics_suffix

def get_title_openai(client,args):

    with open('data/prompt/prompt_{}.md'.format(args.prompt_version), 'r', encoding='utf-8') as file:
        prompt = file.read()

    with open("data/tools.json", 'r') as file:
        # 使用json.load读取文件内容，转换成Python的数据结构
        tools = json.load(file)

    tool_choice = {
        "type":"function",
        "function": {"name": "titles"}
    }

    messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "主题为：{}".format(args.theme)}
        ]
    
    completion = client.chat.completions.create(
            model=args.llm,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice
        )

    tool_call = completion.choices[0].message.tool_calls[0]
    result = json.loads(tool_call.function.arguments)

    messages.append({
                "role": "assistant",
                "content": str(completion),
        })
    messages.append({
                "tool_call_id": tool_call.id,
                "role": "function",
                "name": tool_call.function.name,
                "content": None #需要用户填写
        })
    return result['标题列表'], messages

def get_title_image_langchain(client,system_prompt,description):

    tool_choice = {
        "type":"function",
        "function": {"name": "abstraction"}
    }
    
    prompt = "多张图片描述：{}".format(description)
    response = client.get_text(system_prompt,prompt,tool_choice)
    abstraction = response['text'][0]['args']['故事概要']
    
    tool_choice = {
    "type":"function",
    "function": {"name": "titles"}
    }
    
    prompt = "修改后的故事概要：{}".format(abstraction)
    response = client.get_text(system_prompt,prompt,tool_choice)
    
    return response['text'][0]['args']['标题列表']

def get_title_langchain(client,system_prompt,theme):


    tool_choice = {
        "type":"function",
        "function": {"name": "titles"}
    }
    response = client.get_text(system_prompt,theme,tool_choice)
    
    return response['text'][0]['args']['标题列表']

def get_content_from_title_langchain(client,system_prompt,title):

    tool_choice = {
        "type":"function",
        "function": {"name": "xhs_creator"}
    }
    response = client.get_text(system_prompt,title,tool_choice)
    result = response['text'][0]['args']

    result['正文'] = remove_hash_and_asterisk(result['正文'])
    
    return result

def get_content_from_suggestion_langchain(client,system_prompt,suggestion):

    tool_choice = {
        "type":"function",
        "function": {"name": "xhs_creator"}
    }
    response = client.get_text(system_prompt,suggestion,tool_choice)
    result = response['text'][0]['args']

    result['正文'] = remove_hash_and_asterisk(result['正文'])
    
    return result

def get_content_from_message_openai(client,args,messages):

    with open("data/tools.json", 'r') as file:
        # 使用json.load读取文件内容，转换成Python的数据结构
        tools = json.load(file)

    tool_choice = {
        "type":"function",
        "function": {"name": "xhs_creator"}
    }

    completion = client.chat.completions.create(
            model=args.llm,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice
    )
    for ith_tool, tool in enumerate(completion.choices[0].message.tool_calls, 1):

        result = json.loads(tool.function.arguments)

    result['正文'] = remove_hash_and_asterisk(result['正文'])
    print("文本内容生成成功")
    return result

def get_content_from_theme_openai(client,args):

    with open('data/prompt/prompt_{}.md'.format(args.prompt_version), 'r', encoding='utf-8') as file:
        prompt = file.read()

    function_definition = {
            "name" : "xhs_creator",
            "description": "根据标题，正文，Tags组成小红书完整推文",
            "parameters":{
                "type":"object",
                "properties":{
                    "标题":{
                        "type":"string",
                    },
                    "正文":{
                        "type":"string",
                    },
                    "Tags":{
                        "type":"string",
                    },
                },
                "required": ["标题", "正文", "Tags"]
            }
        }
    tool_choice = {
        "type":"function",
        "function": {"name": "xhs_creator"}
    }
    completion = client.chat.completions.create(
    model=args.llm,
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": "请生成主题为“{}”的小红书推文".format(args.theme)}
    ],
    tools=[
        {"type":"function", "function":function_definition}
    ],
    tool_choice=tool_choice,
    )
    for ith_tool, tool in enumerate(completion.choices[0].message.tool_calls, 1):

        result = json.loads(tool.function.arguments)

    result['正文'] = remove_hash_and_asterisk(result['正文'])
    print("文本内容生成成功")
    return result