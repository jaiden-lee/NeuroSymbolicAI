import requests
from bs4 import BeautifulSoup
import re
import sys
sys.path.insert(0, "C:\\Users\\jaide\\Documents\\CodingProjects\\NeuroSymbolicAI\\rag-pipeline")
# The path in this line needs to change based on path to RAG-pipeline on your machine
from rag_pipeline import RAG

class ArxivRAG:
    def __init__(self, uri, collection):
        self.collection = collection
        paper = requests.get(uri)
        if (paper.status_code != 200):
            print("Error retrieving paper")
            return
        soup = BeautifulSoup(paper.content, "html.parser")

        page_content = soup.select_one(".ltx_page_content")

        title = page_content.select_one("h1.ltx_title").text.replace('\n', '')
        title = "Title: "+title

        authors = page_content.select_one(".ltx_personname").text.replace("start_FLOATSUPERSCRIPT", "").replace("end_FLOATSUPERSCRIPT","")
        authors = re.sub(r"\d", "", authors).replace("*", '').replace('{}','').replace('^',"").replace("\\And","").replace("\n","")
        authors = "Authors: " + authors

        abstract = page_content.select_one(".ltx_abstract").text
        
        paragraphs = [i.text for i in page_content.select(".ltx_section .ltx_para p")]

        self.rag = RAG()
        self.rag.add_documents(self.collection, [title] + [authors] + [abstract] + paragraphs)
    
    def query(self, prompt, num_docs=5, tokens=512):
        return self.rag.rag_query(self.collection, prompt, num_docs,tokens)