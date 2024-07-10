# Simple Agent
All the files in this directory were purely used for playing around and testing agents, however there is no production ready code in here. 

`agent.py` contains code for a simple ReAct + Reflexion agent, though the performance is not that good.

`agent_evaluation.json` is a small dataset to evaluate agents using an LLM as a judge. `evaluate_agent.ipnyb` contains code teo evaluate the agent.py file. `evaluation_results.json` contains the results of testing on `agent.py`

After I tested with ReAct + Reflexion, I switched over to trying to use function calling.

`function_calling.ipnyb` was me testing around with function calling (OpenAI API style), though all the models I tested did not work well. As a result, I had to specifically prompt the models to actually successfully achieve function calling.

`function_selector.py` purely selects tools based on RAG, and then returns those tools. These tools can be supplied to another function calling model with a lot of tools, which may help the model to select tools from a smaller subset.

The code in `function_agent.ipnyb` was a more successful attempt as calling functions, where I prompted the model and showed it examples (as well as mixing some ReAct prompting), to achieve better results with function calling.
