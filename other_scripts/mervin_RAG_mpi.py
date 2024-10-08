#!/gpfs1/data/mie/felipe/conda/envs/ollama/bin/python

import ollama
import bs4
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,)
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings


import requests
import time
import os
import shutil
import argparse



#quit()

# setup argparse options
parser = argparse.ArgumentParser()
parser.add_argument("--query_text", type=str, help="The query text.", default="Why did Alice shrink?")
parser.add_argument("--model_embeddings", type=str, help="The model for embeddings.", default="all-mpnet-base-v2")
parser.add_argument("--model_llm", type=str, help="The model for ollama.", default="llama2:13b")
parser.add_argument("--glob", type=str, help="The glob for the data.", default="*.md")
args = parser.parse_args()
query_text = args.query_text

#query_text = "Why did Alice shrink?"
DATA_PATH = "data"
CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
{context}
---

Answer the FOLLOWING question based only on the PREVIOUS context:
{question}
"""


print("Query text: ", query_text)
print("Loading the documents and splitting them into chunks...")
start_time = time.time()

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob=args.glob)
    documents = loader.load()
    return documents

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    #document = chunks[10]
    # print(document.page_content)
    # print(document.metadata)
    return chunks

def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks,
#    SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2"),
#   HuggingFaceEmbeddings(model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
   HuggingFaceEmbeddings(model_name="mistralai/Mixtral-8x7B-v0.1",
                          cache_folder="/work/borimcor/temp"),
#                          cache_folder="/work/borimcor/temp"),
    #OllamaEmbeddings(model=args.model_llm),    
    persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")
    return(db)

def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    db = save_to_chroma(chunks)
    return db

def query_chroma(query_text: str, db: Chroma):
    results = db.similarity_search_with_score(query_text, k=3)
    return results

def query_ollama(question, context):
    print("Querying model", args.model_llm, "with question:", question, "and context:", context)
    formatted_prompt = f"Question: {question}\nContext: {context}"
    response = ollama.chat(model=args.model_llm, 
                           messages=[{'role': 'user', 'content': formatted_prompt}],
                           options={"temperature": 0.7})
    return response['message']['content']

def main():
    db = generate_data_store()

    results = (query_chroma(query_text, db))

    #print(results)
    #print("Model information: ", ollama.show(args.model_llm)['details'])
    #quit()

#    if len(results) == 0 or results[0][1] < 0.7:
#        print(f"Unable to find matching results.")
#        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print("Prompt:")
    print(prompt)
    response_text = query_ollama(query_text, prompt)
    print("Answer:")
    print(response_text, "\n")

    sources_name = [doc.metadata.get("source", None) for doc, _score in results]
    sources_index = [doc.metadata.get("start_index", None) for doc, _score in results]
    sources_score = [score for _doc, score in results]

    combined_sources = zip(sources_name, sources_index, sources_score)

    for name, index, score in combined_sources:
        print(name, index, score, sep=":")

    return response_text
main()
