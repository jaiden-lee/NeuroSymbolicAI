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