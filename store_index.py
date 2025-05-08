from src.helper import text_split, download_hugging_face_embeddings, load_excel_file
# from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import Pinecone, ServerlessSpec
# from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Load and process Excel data
excel_data = load_excel_file('Data/company roles.xlsx')  # Returns list of Document objects
text_chunks = text_split(excel_data)
print(text_chunks)
print("Hi ")
embeddings = download_hugging_face_embeddings()

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "domain-decoders-test"
if not index_name in pc.list_indexes():
  pc.create_index(
      name=index_name,
      dimension=384, 
      metric="cosine", 
      spec=ServerlessSpec(
          cloud="aws", 
          region="us-east-1"
      ) 
  ) 

# Embed each chunk and upsert the embeddings into your Pinecone index
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings, 
)
