
from openai import OpenAI

def OpenAIClient(api_key):

    client = OpenAI(api_key=api_key)
    return client