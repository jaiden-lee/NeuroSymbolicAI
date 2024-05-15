# Quick Start on rag_pipeline.py
This file contains 2 classes: DocumentDB and RAG.

DocumentDB is used to create a custom database to store documents. This step is optional when creating a RAG pipeline since the RAG class will automatically create an empty database if no DocumentDB is supplied.

To use the RAG class, simply create an instance of the RAG object:
`rag_object = RAG()`

To begin adding documents to the database, use the `.add_documents(collection, docs)` function, where `collection` is a string and `docs` is a list. For example, `rag_object.add_documents("Collection 1", ["Lorem ipsum dolor...", "The quick brown fox..."])`

Then, to ask the RAG pipeline a question based on the documents, call the `.rag_query(self, collection, prompt, num_documents=3, tokens=512)` function, where `collection` is a string representing the collection name and `prompt` is the question you to ask. By default, the number of documents to fetch is 3, and the max number of output tokens produced by the model is 512.
Here is an example: `output = rag_object.rag_query("Collection 1", "Why did John Smith begin selling plungers?")`

If you would like to see a full example on how to use this class, navigate to the rag_example.ipnyb file.
