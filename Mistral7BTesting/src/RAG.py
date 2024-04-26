# IMPORTS
from llama_cpp import Llama
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.document_loaders import AsyncChromiumLoader

from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.llms import LlamaCpp
from langchain.chains import LLMChain
import nest_asyncio
from huggingface_hub import hf_hub_download


nest_asyncio.apply()

articles = ["https://www.fantasypros.com/2023/11/rival-fantasy-nfl-week-10/",
            "https://www.fantasypros.com/2023/11/5-stats-to-know-before-setting-your-fantasy-lineup-week-10/",
            "https://www.fantasypros.com/2023/11/nfl-week-10-sleeper-picks-player-predictions-2023/",
            "https://www.fantasypros.com/2023/11/nfl-dfs-week-10-stacking-advice-picks-2023-fantasy-football/",
            "https://www.fantasypros.com/2023/11/players-to-buy-low-sell-high-trade-advice-2023-fantasy-football/"]

print("hi")
# Scrapes the blogs above
loader = AsyncChromiumLoader(articles)
docs = loader.load()
print("hello")
# Converts HTML to plain text 
html2text = Html2TextTransformer()
docs_transformed = html2text.transform_documents(docs)

# Chunk text
text_splitter = CharacterTextSplitter(chunk_size=100, 
                                      chunk_overlap=0)
chunked_documents = text_splitter.split_documents(docs_transformed)

# Load chunked documents into the FAISS index
db = FAISS.from_documents(chunked_documents, 
                          HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2'))

# Connect query to FAISS index using a retriever
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={'k': 4}
)



prompt_template = """
### [INST] 
Instruction: Answer the question based on your 
fantasy football knowledge. Here is context to help:

{context}

### QUESTION:
{question} 

[/INST]
 """

model_name = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
model_file = "mistral-7b-instruct-v0.2.Q2_K.gguf"
model_path = hf_hub_download(model_name, filename=model_file)

mistral_llm = LlamaCpp(
    model_path=model_path,
    temperature=.2,
    max_tokens=300,
    n_ctx=1000
)

# Create prompt from prompt template 
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=prompt_template,
)

# Create llm chain 
llm_chain = LLMChain(llm=mistral_llm, prompt=prompt)
print(llm_chain.invoke({"context": "", "question": "Should I start Gibbs in week 16 for fantasy?"}))

# Make RAG chain
rag_chain = ( 
 {"context": retriever, "question": RunnablePassthrough()}
    | llm_chain
)

result = rag_chain.invoke("Should I start Gibbs next week for fantasy?")

print(result['text']) # this took prob like 20 minutes or smth, but no context was prob like less than 5 minutes, but it works