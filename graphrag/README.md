I'm just taking notes for now:

GraphRAG is originally meant for OpenAI/Azure. But, as long as whatever I'm using is OpenAI API compatible, then it should work.

Ollama seems to have issues since it doesn't have embeddings API support yet. However, GraphRAG requires both completions and embeddings. I believe the embeddings model can be different than the LLM, since the embeddings is used to embed the text and convert it to a graph, not the actual inferencing itself. 

vLLM also doesn't have support for embeddings API yet either idt.

LLama.cpp python, when I tested the inference server, seems to have support for embeddings api, so I should just be able to use it. I am planning to use just the same model, just for simplicity, though maybe I should change it to a lighter model. So I should be fine when using Llama.cpp

The settings.yaml file also contains an encoding_model property at the top. Not completely sure what this does and if it is different from embeddings.


My current understanding of how the graph works: document split into textunits, which are split into semantic triples
These semantric triples are added to graph, and then they are turned into clusters called communities, which get their own metadata (summary)
Semantric triples also have reference to the original documents it seems, though not completely sure what it does with these

Apparently there are 2 graphs? entity-relationship graph, and document graph