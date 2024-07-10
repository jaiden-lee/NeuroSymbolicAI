# Arxiv RAG
### Overview
The file `arxiv_rag.py` contains the class `ArxivRAG` which allows you to upload an arxiv paper HTML link, and it can perform RAG on it.

The file arxiv_text.ipnyb just showcases the ArxivRAG class in action.

### Usage Guide
To use the ArxivRAG class, create a new instance of the object. As parameters, first supply the URL to the Arxiv paper. Make sure it is an HTML link, not a PDF, or else the webscraping will not work. Then, you need to supply a collection name. The collection name follows ChromaDB colleciton naming standards, so the first character should be a letter, and there should be no spaces. The collection is where the documents are stored after scraping the paper.

`rag = ArxivRAG(URL_LINK, COLLECTION_NAME)`

After, just call the `query(prompt, num_docs, tokens)` method. The num_docs and tokens are optional to supply, but prompt is necessary - it is the question you want to ask about the paper.
