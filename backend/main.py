import sys
import os

# Add the project root to the python path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.agents.orchestrator import handle_request

load_dotenv()

app = FastAPI(title="Chaldal AI Multi-Agent System")

# Configure CORS - Allow all origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now, restrict in production if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        response = handle_request(request.message)
        return {"response": response}
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to Chaldal AI Backend"}
