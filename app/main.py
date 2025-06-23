from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .client import chat_with_groq, save_conversation, load_conversation
from .config import HOST, PORT, DEBUG, CONVERSATIONS_DIR
from typing import Optional, Dict, Any
import os
import json
import uuid

# Create conversations directory if it doesn't exist
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

app = FastAPI(
    title="Coding Copilot API",
    description="API for interacting with the Coding Copilot powered by Groq",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request) -> Dict[str, Any]:
    try:
        data = await request.json()
        user_input = data.get("message")
        conversation_id = data.get("conversation_id")
        
        if not user_input:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Load existing conversation if conversation_id is provided
        conversation_history = None
        if conversation_id:
            conversation_file = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
            try:
                if os.path.exists(conversation_file):
                    conversation_history = load_conversation(conversation_file)
            except Exception as e:
                print(f"Error loading conversation: {str(e)}")
                conversation_history = None
        
        # Get response from Groq
        response, updated_history = chat_with_groq(user_input, conversation_history)
        
        # Generate a conversation ID if it doesn't exist
        if not conversation_id:
            conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        
        # Always save the updated conversation
        try:
            save_conversation(updated_history, os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json"))
        except Exception as e:
            print(f"Error saving conversation: {str(e)}")
        
        return {
            "response": response,
            "conversation_id": conversation_id
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG
    )