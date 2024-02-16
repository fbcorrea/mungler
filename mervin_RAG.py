#!/gpfs1/data/mie/felipe/conda/envs/ollama/bin/python

# Importing libraries
print("importing libraries...")
import ollama
#import bs4
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,)
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

import re
import requests
import time
import os
import shutil
import argparse

print("setting up argparse")
# setup argparse options
parser = argparse.ArgumentParser()
parser.add_argument("--query_text", type=str, help="The query text.", default="Why did Alice shrink?")
#parser.add_argument("--model_embeddings", type=str, help="The model for embeddings.", default="all-mpnet-base-v2")
parser.add_argument("--model_embeddings", type=str, help="The model for embeddings.", default="Salesforce/SFR-Embedding-Mistral")
parser.add_argument("--model_llm", type=str, help="The model for ollama.", default="llama2")
parser.add_argument("--glob", type=str, help="The glob for the data.", default="*.md")
args = parser.parse_args()
query_text = args.query_text

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

def clean_text(text):
    # Replace line breaks with a space if they don't follow a period
    cleaned_text = re.sub(r"(?<!\.)\n", " ", text)
    # Remove any instances of multiple spaces with a single space
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    # Remove empty lines
    cleaned_text = re.sub(r"\n\s*\n", "\n", cleaned_text)
    return cleaned_text.strip()

def split_text(documents: list[Document]):
    print("cleaning text...")
    # Iterate in list of documents and clean the text
    for doc in documents:
        # clean the text
        doc.page_content = clean_text(doc.page_content)
    print("splitting text...")
    # Split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    # db = Chroma.from_documents(documents=chunks,
    #                             embedding=SentenceTransformerEmbeddings(model_name=args.model_embeddings,
    #                                                                     cache_dir="/work/borimcor/cache"),
    #                             persist_directory=CHROMA_PATH)
    db = Chroma.from_documents(documents=chunks,
                                embedding=HuggingFaceEmbeddings(
                                    model_name=args.model_embeddings,
                                    cache_folder="/work/borimcor/cache"),
                                persist_directory=CHROMA_PATH)
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")
    return(db)

def generate_data_store():
    print("loading documents...")
    documents = load_documents()
    print("splitting into chunks...")
    chunks = split_text(documents)
    print("embedding chunks and saving to db...")
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
                           options={"temperature": 0.9})
    return response['message']['content']

def main():
    # print gerating data store using model_embeddings
    print("generating data store using ", args.model_embeddings, "...   ")
    db = generate_data_store()
    print("querying database...")
    results = (query_chroma(query_text, db))
    
    print(results)

    if len(results) == 0 or results[0][1] < 0.6:
        print(f"Unable to find matching results.")
        return

    print("generating prompt...")
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

    # Add code to save the response text to a file
    with open("response.txt", "w") as file:
        file.write(response_text)
        print("Response saved to response.txt")

    return response_text
main()