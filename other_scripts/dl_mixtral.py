from langchain_community.embeddings import HuggingFaceEmbeddings

print("trying to download...")
HuggingFaceEmbeddings(model_name="mistralai/Mixtral-8x7B-v0.1",cache_folder="/work/borimcor/temp")
#HuggingFaceEmbeddings(model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",cache_folder="/work/borimcor/temp")
