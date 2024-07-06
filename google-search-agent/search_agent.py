from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import json
import re
from dotenv import load_dotenv
import os
import requests
load_dotenv()

GCP_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
base_url = "https://www.googleapis.com/customsearch/v1?"

class SearchAgent:
    def __init__(self):
        model_name = "bartowski/Mistral-7B-Instruct-v0.3-GGUF"
        model_file = "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
        model_path = hf_hub_download(model_name, filename=model_file)
        self.model = Llama(
            model_path = model_path,
            n_ctx=32000,
            verbose=False
        )
        self.search_prompt = search_prompt = """
You are a helpful assistant with only 1 job:
1) Search the internet

Always includes a THOUGHT, and a RESPONSE. Afterwards, return the PAUSE keyword.

Whenever asked a question, break down the question step by step. Figure out what information you need to answer the question.

###EXAMPLE 1:
User: Who is the current president of the United States?

THOUGHT: This is a simple question, I just need to look up who the current president of the United States is.
RESPONSE: current president of the United States
PAUSE
###END EXAMPLE 1

###EXAMPLE 2:
User: What is the largest animal in the world?

THOUGHT: I can simply look up the largest animal in the world
RESPONSE: largest animal in the world
PAUSE
###END EXAMPLE 2
"""
        self.answer_prompt = """
You are a helpful assistant with access to the provided context below. You may or may not need to use the provided context.

Do not directly restate the context provided, but rather, rephrase the context into your own words and explain the context to the user.
"""

    def query(self, question, verbose=False):
        prompt = f"""
[SYSTEM]
{self.search_prompt}

[USER]
{question}

[ASSISTANT]
THOUGHT: 
"""
        search_query = None
        output = self.model(prompt, max_tokens=512, stop=["PAUSE"])["choices"][0]["text"]
        # parses output to get the search query
        for line in output.split("\n"):
            response_regex = "RESPONSE: (.*)"
            found_response = re.search(response_regex, line)
            if found_response:
                search_query = found_response.group(1)
                break
        
        # performs the API call; if model produced good output, it will use it as query; otherwise, just use question
        docs = []
        params = {
            "key": GCP_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": search_query if search_query else question
        }
        res = requests.get(base_url, params)
        data = res.json()
        items = data["items"]
        i = 0
        while i < 3 and i < len(items):
            docs.append({"text": items[i]["snippet"], "source": items[i]["displayLink"]})
            i+=1
        
        prompt = f"""
[SYSTEM]
{self.answer_prompt}

###CONTEXT:
{docs}

[USER]
{question}

[ASSISTANT]
"""
        output = self.model(prompt, max_tokens=512, stop=["PAUSE"])["choices"][0]["text"]
        if verbose:
            print(docs)
            print(search_query)
        return output
    
class SearchSelectAgent:
    def __init__(self):
        model_name = "bartowski/Mistral-7B-Instruct-v0.3-GGUF"
        model_file = "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
        model_path = hf_hub_download(model_name, filename=model_file)
        self.model = Llama(
            model_path = model_path,
            n_ctx=32000,
            verbose=False
        )
        self.system_prompt = """
You are an AI assistant with only 2 jobs:
1) call a tool
2) respond to the user

Only perform on of these actions at a time. Either call a tool, or respond to the user. 

Your response must always include a THOUGHT and a RESPONSE keyword, and then you must follow it with the PAUSE keyword.

All of your outputs should be in JSON format. If you call a function, then output your response in the following JSON schema:
RESPONSE: {"tool_name": "the name of the tool", "parameters": {"parameter1": "value1", "parameter2": "value2"}}

If you do not call a function and answer the user, then output your response in the following JSON schema:
RESPONSE: {"message": "the message to display to the user"}

DO NOT include "message" if you call a tool. DO NOT include "tool_name"or "parameters" if you do not call a tool.

Call AT MOST ONE tool at a time.

If you call a tool, you will be provided with a RESULT that provides the result of the tool call.

Here are some examples:

###EXAMPLE 1:
Provided tools: 
{"name": "get_location", "description": "Get the user's location", "parameters": {"type": "object", properties: {}}

User: What is my location?

THOUGHT: I need to get the user's location.
RESPONSE: {"tool_name": "get_location", "parameters": {}}
PAUSE

RESULT: {"location": "New York City, NY"}

THOUGHT: Now that I have the user's location, I can respond to the user
RESPONSE: {"message": "Your current location is New York City."}
PAUSE
###END EXAMPLE 1

###EXAMPLE 2:
Provided tools:
{"name": "get_location", "description": "Get the user's location", "parameters": {"type": "object", properties: {}}
{"name": "internet_search", "description": "Perform an internet search and returns the result of the search", "parameters": {"type": "object", properties: {"query": {"type": "string", "description": "the question to ask the search engine"}}, "required": ["query"]}}

User: What are some places to eat nearby?

THOUGHT: To recommend places to eat, I first need to get the user's location
RESPONSE: {"tool_name": "get_location", "parameters": {}}
PAUSE

RESULT: {"location": "Irvine, CA"}

THOUGHT: Now that I know the user lives in Irvine, CA, I now need to perform an internet search to restaurants in Irvine.
RESPONSE: {"tool_name": "internet_search", "parameters": {"query": "Restaurants in Irvine, CA"}}
PAUSE

RESULT: {"search_result": "Some restaurants include: In N' Out, Urban Plates, and iCafe"}

THOUGHT: I have enough information to respond to the user.
RESPONSE: {"message": "In Irvine, CA, some restaurant recommendations are In N' Out, Urban Plates, and iCafe."}
PAUSE
###END EXAMPLE 2



PROVIDED TOOLS:
{"name": "internet_search", "description": "Perform an internet search and returns the result of the search.", "parameters": {"type": "object", properties: {"query": {"type": "string", "description": "the question to ask the search engine"}}, "required": ["query"]}}
"""
        self.actions = {
            "internet_search": self.internet_search
        }

    def internet_search(self, query):
        docs = []
        params = {
            "key": GCP_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": query
        }
        res = requests.get(base_url, params)
        data = res.json()
        items = data["items"]
        i = 0
        while i < 3 and i < len(items):
            docs.append({"text": items[i]["snippet"], "source": items[i]["displayLink"]})
            i+=1
        return docs

    def query(self, question):
        prompt = f"""
[SYSTEM]
{self.system_prompt}

[USER]
{question}

[ASSISTANT]
THOUGHT: 
"""
        for _ in range(10):
            output = self.model(prompt, max_tokens=512, stop=["PAUSE", "Pause", "THOUGHT", "Thought", "RESULT", "Result"], temperature=1)
            output_str = output["choices"][0]["text"]
            response_regex = "RESPONSE: (.*)"
            foundResponse = re.search(response_regex, output_str)
            if foundResponse:
                response_json={}
                try:
                    response_json = json.loads(foundResponse.group(1))
                except:
                    print("Error")
                    pass
                # Message found, return
                if "message" in response_json:
                    prompt += output_str
                    return response_json["message"]
                # calls a tool
                elif "tool_name" in response_json: 
                    print(response_json)
                    prompt += output_str
                    tool_name = response_json["tool_name"]
                    params = {}
                    if "parameters" in response_json:
                        params = response_json["parameters"]
                    tool_result = None
                    if len(params) > 0:
                        tool_result = self.actions[tool_name](**params)
                    else:
                        tool_result = self.actions[tool_name]()
                    prompt += f"\nRESULT: {tool_result}\nTHOUGHT: "
                    print("___________________________________________________________________________")
                    print(prompt)