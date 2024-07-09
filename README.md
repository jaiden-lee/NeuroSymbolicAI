# NeuroSymbolicAI

## Installation/Setup Instructions (Windows)
### Step 1. Clone repo onto your local machine
### Step 2. Once installed, create a virtual environment.
Type: "python3 -m venv .venv" in the command line in the root directory to create a virtual environment called ".venv"
### Step 3. After setting up the virtual environment, run/launch the virtual environment
Navigate to the Scripts and run the virtual environment. It depends on which terminal and operating system you are using, but it will be a file called **activate** plus some file extension (i.e., .bat for windows CMD, or .ps1 for windows powershell)

If you're on Mac or Linux, type `source activate`
### Step 4. Once the venv is launched, navigate to the root directory and install dependencies.
**Windows**: Run `pip3 install -r requirements.txt` from the root of the project

**Mac**: Run `pip3 install -r macrequirements.txt` from the root of the project

To verify everything has been installed, you can type `pip3 list`

Everything should now be setup properly.

## Navigating the Codebase
### Mistral7BTesting
This code contains the code related to testing and prototyping with the Mistral 7B model. I primarily used this directory when I was learning, though I do not really update this directory much anymore. 

The **prototyping.ipynb** file was for testing the pure Mistral7B (unquantized) model, which is very slow.

The **quantization.ipnyb** file is for testing with a GGUF quantized version of Mistral7B run using Llama.cpp for python. 

**RAG.ipnyb** currently doesn't function properly since langchain async requests cannot be made in jupyter notebooks for some reason, and I can't figure out how to get around that

**RAG.py** is where I followed a tutorial on using langchain to build RAG model. It is very slow as well, even though I'm also using a quantized model.
### rag-pipeline
The main file in this directory is rag_pipeline.py

By importing this file into another file, you can instantiate a RAG object. Example code is provided in the rag_example.ipnyb file. 

More documentation is provided in the README file inside the rag-pipeline directory.

### arxiv-rag
This code contains a class that is able to take in a research paper from arxiv in HTML format, and perform RAG on it.

One caveat, you must use a different collection name for each different arxiv article; (I will try to fix this in the future, but it appears that new ChromaDB objects don't create new databases, rather it just points to the same cached database).

Other than that, it's really easy to use. Simply just instantiate the ArxivRAG object and initialize with the URL to the arxiv html page, as well as the collection name. Then, just call the .query() method to ask the model questions.

### llm-judge-context-dataset
This directory contains a .json file, which serves as a small dataset to evaluate a model's performance.

### simple-agent
I was primarily using this directory to play around with creating agents using techniques like ReACT, Reflexion, and function calling. However, most of the code here isn't production quality and is mainly prototyping. No initial setup is needed to get the code in this directory working.

### google-search-agent
This directory contains the `search_agent.py` file, which contains 2 classes that are used to perform google search queries. You can find more detail in the README.md file in that directory.
