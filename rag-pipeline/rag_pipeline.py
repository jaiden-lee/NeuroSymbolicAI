import chromadb
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

class DocumentDB:
    def __init__(self):
        self.db = chromadb.Client()
        self.num_docs = 0

    def add_collection(self, name):
        self.db.get_or_create_collection(name)

    def add_documents(self, collection, docs):
        ids = [str(i) for i in range(self.num_docs, self.num_docs + len(docs))]
        self.db.get_or_create_collection(collection).add(documents = docs, ids = ids)
        self.num_docs += len(docs)
        
    def retrieve_documents(self, collection, prompt, num_documents=3):
        return self.db.get_collection(collection).query(query_texts = prompt, n_results=num_documents)

class RAG:
    def __init__(self, db=None):
        if db is None:
            db = DocumentDB()
        self.db = db
        model_name = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
        model_file = "mistral-7b-instruct-v0.2.Q2_K.gguf"
        model_path = hf_hub_download(model_name, filename=model_file)
        self.model = Llama(
            model_path = model_path,
            n_ctx=4096
        )

    def add_collection(self, name):
        self.db.add_collection(name)

    def add_documents(self, collection, docs):
        self.db.add_documents(collection, docs)
    
    def query(self, prompt, tokens):
        output = self.model(
            prompt = prompt,
            max_tokens = tokens,
            stop = ["Q:"],
            echo=False
        )
        output_text = output['choices'][0]['text']
        return output_text

    def retrieve(self, collection, prompt, num_documents=3):
        docs = self.db.retrieve_documents(collection, prompt, num_documents)
        docs_text = docs['documents'][0]
        return docs_text

    def rag_query(self, collection, prompt, num_documents=3, tokens=512):
        docs = self.retrieve(collection, prompt, num_documents)
        context = context = "\n".join(docs)
        input = f"""
                ### [INST] 
                Answer the following question based on your current knowledge, as well as the following information provided:

                {context}

                ### QUESTION:
                {prompt} 

                [/INST]
                """
        output = self.query(input, tokens)
        return output