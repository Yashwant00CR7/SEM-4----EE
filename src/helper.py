from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
import pandas as pd
from langchain.docstore.document import Document


#Extract Data From the PDF File
def load_pdf_file(data):
    loader= DirectoryLoader(data,
                            glob="*.pdf",
                            loader_cls=PyPDFLoader)

    documents=loader.load()

    return documents



#Load Data From Excel File
def load_excel_file(file_path):
    df = pd.read_excel(file_path)
    documents = []
    
    for _, row in df.iterrows():
        # Create a text representation of each row
        text = f"Company: {row['Company']}\nRole: {row['Roles']}\nResponsibilities: {row['Responsibilities']}\nLanguage: {row['Language']}\nEssential Knowledge: {row['Essential Knowledge']}\nExperience Required: {row['Experience Required']}\nLevel of Role: {row['Level of Role']}\nPackage Details: {row['Package Details (LPA)']}"
        
        # Create a Document object with metadata
        doc = Document(
            page_content=text,
            metadata={
                'company': row['Company'],
                'role': row['Roles'],
                'package': row['Package Details (LPA)']
            }
        )
        documents.append(doc)
    
    return documents



#Split the Data into Text Chunks
def text_split(extracted_data):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks=text_splitter.split_documents(extracted_data)
    return text_chunks



#Download the Embeddings from HuggingFace 
def download_hugging_face_embeddings():
    embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')  #this model return 384 dimensions
    return embeddings