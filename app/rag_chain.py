# app/rag_chain.py
import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.pgvector import PGVector
from langchain.chains import ConversationalRetrievalChain

load_dotenv()

# --- CORRECTED DATABASE CONNECTION BLOCK ---
# We access credentials directly. If a variable is missing in the .env file,
# the app will raise a KeyError and stop, which is the desired, secure behavior.
try:
    CONNECTION_STRING = PGVector.connection_string_from_db_params(
        driver=os.environ.get("DB_DRIVER", "psycopg2"), # A default here is acceptable
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
except KeyError as e:
    raise ValueError(f"Missing mandatory environment variable: {e}") from e
# ----------------------------------------------


# In-memory store for session memories
chat_memory_store = {}

def get_session_memory(session_id: str) -> ConversationBufferMemory:
    """Retrieves or creates a memory buffer for a given session ID."""
    if session_id not in chat_memory_store:
        chat_memory_store[session_id] = ConversationBufferMemory(
            memory_key='chat_history', return_messages=True
        )
    return chat_memory_store[session_id]

# --- RAG Core Functions ---

def process_and_store_docs(file_paths: list, collection_name: str):
    """Loads, splits, and stores documents in a persistent PGVector database."""
    print(f"Processing documents for collection: {collection_name}")
    all_docs = [doc for path in file_paths for doc in PyPDFLoader(path).load()]
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(all_docs)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        connection_string=CONNECTION_STRING,
    )
    print("Documents embedded and stored successfully.")

def get_conversational_rag_chain(collection_name: str, memory: ConversationBufferMemory):
    """Initializes and returns a conversational RAG chain."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    vectorstore = PGVector(
        connection_string=CONNECTION_STRING,
        collection_name=collection_name,
        embedding_function=embeddings,
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
    )