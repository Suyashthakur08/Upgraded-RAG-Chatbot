# app/main.py

import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from .rag_chain import process_and_store_docs, get_session_memory, get_conversational_rag_chain
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# --- Path and App Setup ---
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
TEMP_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "temp_uploads")
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="RAG Chatbot API",
    description="API for a RAG chatbot powered by LangChain and Gemini.",
    version="2.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str

# --- API Endpoints ---

@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(STATIC_DIR, 'index.html'))

app.mount("/frontend", StaticFiles(directory=STATIC_DIR), name="frontend")

# --- CORRECTED UPLOAD ENDPOINT ---
@app.post("/upload", response_model=ChatResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    # The backend is now fully responsible for creating the session ID on upload.
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    file_paths = []
    for file in files:
        # We save the file temporarily to be read by PyPDFLoader
        file_path = os.path.join(TEMP_UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        file_paths.append(file_path)
    
    try:
        # The collection_name for the vector store is the session_id,
        # linking the documents directly to this specific chat session.
        process_and_store_docs(file_paths, collection_name=session_id)
        
        # Clean up the temporary files after processing
        for path in file_paths:
            os.remove(path)
            
        # Return a helpful message and the new session_id
        return ChatResponse(
            answer="Files processed successfully! You can now start chatting.",
            session_id=session_id
        )
    except Exception as e:
        print(f"Upload error: {e}")
        # Clean up files even if processing fails
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_with_rag(request: ChatRequest):
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required for chat.")
    
    try:
        memory = get_session_memory(request.session_id)
        rag_chain = get_conversational_rag_chain(request.session_id, memory)
        
        response = await rag_chain.ainvoke({"question": request.query})
        
        return ChatResponse(answer=response['answer'], session_id=request.session_id)
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))