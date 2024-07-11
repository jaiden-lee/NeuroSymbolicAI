# LLM Judge Context Dataset
This dataset is meant to be used when testing **RAG** pipelines. Specifically, it is meant to test the effectiveness of a model at taking provided context, and producing an output based on that given context, not the retrieval algorithm of the RAG pipeline.

Although there is no code to directly test the dataset, it is pretty easy to get started. You first just need to load the json file.
```
import json
with open("dataset.json") as json_data:
    data = json.load(json_data)
data = data["data"]
```

This will load the data is a python dictionary.

Afterwards, you can loop through the dictionary and evaluate the model. 

Make sure your initial prompt includes the context from the `context` attribute, as well as the `prompt` attribute. Also, make sure to test whether or not the question can be answered based on the context, as seen with the `canAnswer` property.

When evaluating, make sure to use LLM as a judge. 

An example of evaluating one entry could go like this:
1. Append the `context` to the prompt as well as the `prompt`
2. Feed the prompt to a model, and record the output
3. Feed both the output to another model, and ask that new model to rate the output on a scale from 1-10, as well as to fail the model of the output is 1. Showing few-shot examples would be helpful here.
4. Record the model output
