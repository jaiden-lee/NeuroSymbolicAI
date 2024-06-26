import chromadb
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

class FunctionSelector:
    def __init__(self):
        self.db = chromadb.Client()
        self.system_prompt = """
You are an assistant with only 1 jobs:
1) Call a tool.

You will be asked a question by the user. All of your outputs should contain a THOUGHT and at least one TOOL. You can call up to 3 TOOLS at a time. Afterwards, return PAUSE.

Whenever asked a question, break down the question step by step. Figure out what type of tool can best assist you to answer the question.

###EXAMPLE 1:
User: Can you give me a name for my new child?

THOUGHT: I need to know the gender of the child. 
TOOL: A tool to find the gender of the child.
PAUSE

###EXAMPLE 2:
User: If it is sunny outside, is it usually warm or cold?

THOUGHT: I have multiple choices. I can call a tool that answers reasoning questions. I can also call a tool that performs an internet search.
TOOL: A tool that answers reasoning questions
TOOL: A tool that performs internet search.
PAUSE
###END EXAMPLE 2

###EXAMPLE 3:
User: What is my current location?

THOUGHT: I need the user's current location. I can answer this with a tool that gets the users location.
TOOL: Tool that gets the users location.
PAUSE
###END EXAMPLE 3

###EXAMPLE 4:
User: What are some activities to do based on the weather outside?

THOUGHT: In order to recommend activities, I need to get the weather outside.
TOOL: Tool that gets the weather at the user's location.
PAUSE
###END EXAMPLE 4
"""
        self.tools_collection = self.db.get_or_create_collection("Tools")

        model_name = "bartowski/Mistral-7B-Instruct-v0.3-GGUF"
        model_file = "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
        model_path = hf_hub_download(model_name, filename=model_file)
        self.model = Llama(
            model_path = model_path,
            n_ctx=32000
        )

    def add_tool(self, tool_name, description):
        tool = f"""{tool_name}
Description: {description}
"""
        self.tools_collection.add(ids = [tool_name], documents = [tool])
    
    def add_tools(self, tools):
        tool_prompts = []
        tool_names = []
        for tool in tools:
            tool_name = tool["tool_name"]
            tool_desc = tool["description"]
            tool_names.append(tool_name)
            tool_prompts.append(
f"""{tool_name}
Description: {tool_desc}
"""
            )
        self.tools_collection.add(ids = tool_names, documents = tool_prompts)

    def select_function(self, query):
        prompt = f"""
[SYSTEM]
{self.system_prompt}

[USER]
{query}
"""
        res = self.model(prompt, stop=["PAUSE"], echo=False, max_tokens = 512)
        output = res["choices"][0]["text"]
        tool_calls = []
        print(output)
        for line in output.split("\n"):
            if "TOOL" in line:
                tool = self.tools_collection.query(query_texts=line, n_results=1)
                tool_calls.append(tool)
        return tool_calls