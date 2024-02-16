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

import requests
import time
import os
import shutil
import argparse