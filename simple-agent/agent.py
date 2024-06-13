import sys
sys.path.insert(0, "C:\\Users\\jaide\\Documents\\CodingProjects\\NeuroSymbolicAI\\arxiv-rag")
from arxiv_rag import ArxivRAG
import re


class Agent:
    def __init__(self, uri):
        # To make it easy for now, I'm just going to use the model that comes with the arxiv-rag system
        self.uri = "https://arxiv.org/html/2306.05685v4" # change to uri later
        self.agent = ArxivRAG(uri, "llm-judge")
        self.system_prompt = """
You cycle through Thought, Action, PAUSE, Observation. When you have enough information, output your final answer. Your final answer should be highly specific to the observations you have from running the actions.
1. Thought: Describe your thoughts about the question you have been asked.
2. Action: run one of the actions available to you - then return PAUSE.
3. PAUSE
4. Observation: will be the result of running those actions.

Available actions:
- retrieveDocuments:
    E.g. retrieveDocuments: Who are the authors of the MTBench paper?
    Returns a collection of documents about the paper MTBench LLM Judge paper.
- calculator:
    E.g. calculator: 5+10
    Returns the answer to the provided math equation. 
- convertToWordProblem:
    E.g. convertToWordProblem: Bob has 5 friends. He buys 3 apples for each of his friends. How many apples does he have to buy?
    Converts the provided word problem into a math equation.

Example session 1:
Question: Bob has 5 bananas. He eats 2 of them. How many does he have left?.
Thought: I am being provided a word problem. I should turn this word problem into an equation. 
Action: convertToWordProblem: Bob has 5 bananas. He eats 2 of them. How many does he have left?
PAUSE

Observation: 5-2

Action: calculator: 5-2
PAUSE

Observation: 3

Answer: Bob has 3 apples left.
PAUSE

Example session 2:
Question: What is the difference between MTBench and Chatbot Arena?
Thought: I should first find out what MTBench is.
Action: retrieveDocuments: What is MTBench?
PAUSE

Observation: <A set of 5 sentences describing what MTBench is.>

Thought: Now I need to find out what Chatbot Arena is.
Action: retrieveDocuments: What is Chatbot Arena?
PAUSE

Observation: <A set of 5 sentences describing what Chatbot Arena is.>

Answer: <A comparison between MTBench and Chatbot Arena given your newfound knowledge based on the documents provided to you>
PAUSE
"""
        self.evaluation_prompt = """
You will be shown a question and an answer. Give both an Evaluation and a Score. On a scale of 1-10, Score the answer based on its accuracy and how well it answers it the question. Then return PAUSE. Here are 3 examples to help:

Example 1:
Question: What is 5 minus 6
Answer: The operation results in an answer that is not valid since it is negative, and negative numbers are not allowed within the given context of the problem statement.

Evaluation: The previous answer is incorrect. Although 5 minus 6 is negative, the problem does not state that negative numbers are not allowed.
Score: 1
PAUSE

Example 2:
Question: Bob originally had 3 apples. He buys 2 more. How many does he have now?
Answer: Bob has 1 apple left.

Evaluation: The previous answer is incorrect. The number of apples Bob has should increase, since he buys more.
Score: 1
PAUSE

Example 3:
Question: What is Chatbot Arena?
Answer: Chatbot Arena is a platform that allows users to compare and evaluate different AI chatbot builders. It provides side-by-side comparisons of various chatbot tools, ranking them based on features, pricing, and community trust.

Evaluation: The previous answer is highlight specific to the prompt and fully answers the question provided.
Score: 10
PAUSE
"""
        self.reflection_prompt = """
You will be given the history of a past experience in which you were asked a question, as well as an evaluation. You were unsuccessful in answering the question. Think about the strategy and approach you took to attempt to complete the task. Devise a concise, new plan of action that accounts for your mistake with reference to specific actions that you should have taken. For example, if you tried A and B but forgot C, then devise a plan to achieve C. You will need this later when you are solving the same task. Give your plan after "Plan:". Here is an example to help:

Example 1:
Question: What is 5 minus 6?

Thought: This is a simple arithmetic question.
Action: calculator: 5-6

Observation: -1
Answer: The operation results in an answer that is not valid since it is negative, and negative numbers are not allowed within the given context of the problem statement.

Evaluation: The previous answer is incorrect. Although 5 minus 6 is negative, the problem does not state that negative numbers are not allowed.
Score: 1

Plan: I see my mistake. I misread the problem and assumed that the problem did not allow for negative numbers. However, my process for achieving a result of -1 was correct. Next time, I will keep the same process to get to an answer of -1, but I will focus on making sure my answer is specifically tailored to the question being asked.
PAUSE
"""
        self.actions = {}
        self.actions["convertToWordProblem"] = self.convertToWordProblem
        self.actions["calculator"] = self.calculator
        self.actions["retrieveDocuments"] = self.retrieveDocuments
        


    def convertToWordProblem(self, problem):
        prompt = f"""
[SYSTEM]
You will be given a word problem. Convert the word problem into a simple math equation. DO NOT EVALUATE THE EQUATION. You should break down each word problem step by step by providing your own Thought. Here are some examples:

Example 1: 
Problem: Bob has 5 bananas. He eats 2 of them. How many does he have left?.
Thought: Bob originally has 5 bananas. Then, we must take away 2 of the bananas since he eats 2 of them.
Answer: 5-3

Example 2:
Problem: Bob has 5 friends. He buys 3 bananas for each friend. How many bananas does he buy?
Thought: Each one of Bob's friends needs 3 bananas. He has 5 friends.
Answer: 5*3

Example 3:
Problem: Bob has 2 friends and 2 brothers. He needs to buy 4 bananas for each friend, and 3 bananas for each brother. How many bananas does he buy?
Thought: Since Bob has 2 friends and each friend needs 4 bananas, he should buy 2*4 bananas for his friends. Since Bob has 2 brothers and each brother needs 3 bananas, he should buy 2*3 bananas for his brothers.
Answer: 2*4+2*3

[USER]
Problem: {problem}

[ASSISTANT]
        """
        output = self.agent.normal_query(prompt, tokens=512, temp=1)
        regex = "Answer: (.*)$"
        found = re.search(regex, output)
        if found:
            return found.group(1)
        return "Failed to convert to equation. Retry again."
    
    def calculator(self, expression):
        try:
            return eval(expression)
        except:
            return "This was not a valid mathematical expression"
    
    def retrieveDocuments(self, query):
        docs = self.agent.retrieve_docs(query)
        return "[" + ", ".join(docs)+"]"
    
    def query(self, question):
        prompt = f"""
[SYSTEM]
{self.system_prompt}

[USER]
Question: {question}

[ASSISTANT]
"""
        output = ""
        for i in range(10):
            print("_"*20+ "\n" + prompt)
            output = self.agent.normal_query(prompt, tokens=512, temp=1)
            # print(output)

            actionRegex = "Action: (\\w+): (.*)"
            foundAction = re.search(actionRegex, output)
            if "Answer:" not in output and foundAction is not None:
                action = foundAction.group(1)
                params = foundAction.group(2)
                if action in self.actions:
                    func = self.actions[action]
                    res = func(params)
                    # print(res)
                    prompt += f"\n{output}\nObservation: {res}"
            else:
                if "Answer:" in output:
                    print("FOUND ANSWER \n"+"_"*20 +"\n"+output)
                    # evaluate answer now
                    new_prompt = f"""
[SYSTEM]
{self.evaluation_prompt}

[USER]
Question: {question}
Answer: {output}

[ASSISTANT]
"""
                    evaluation = self.agent.normal_query(new_prompt, tokens=512, temp=0)
                    print("_"*20 + "\n" + evaluation)
                    scoreRegex = "Score: (\\d+)"
                    scoreFound = re.search(scoreRegex, evaluation)
                    if scoreFound is not None:
                        score = int(scoreFound.group(1))
                        if (score >= 5):
                            return output
                        # if doesn't pass threshold, then we need to revealuate
                        prompt += f"\n{output}"
                        new_prompt = f"""
[SYSTEM]
{self.reflection_prompt}

{prompt}

[USER]
{evaluation}

[ASSISTANT]
Plan:
"""
                        reflection = self.agent.normal_query(new_prompt, tokens=512, temp=0)
                        prompt += f"""
[USER]
{evaluation}

[ASSISTANT]
Plan: {reflection}

[USER]
Question: {question}

[ASSISTANT]
"""
        return "MODEL FAILED TO PRODUCE OUTPUT"
    
    # bug, even when the model answers, it will generate another question to answer and begin answering that; i noticed that it answers the questions pretty well, but then it hallucinates a new question; I think I need to add a PAUSE statement
    # optimization, model doesn't like to listen to my structure and will keep going even I told it to stop; so, I think the second I see answer, I break out; I should change it to check for answer first, and then for action; I'm not really sure how to get it to stop answering automatically, cuz like even with RAG, it'll just put the document there, which it made up (I'm guessing one of papers it was fine tuned on was MTBench, so it prob knows a good amt about it, but I still want it to pause and take an action instead of just doing whatever it does)
    # I also notice the evaluation isn't that good; false negatives; like the answer is right, but the evaluation keeps saying the model is wrong in its answer
    # on top of the model doing things on its own, it will try to review itself, even when I haven't prompted it to be reviewed yet, and this wasn't in the directions