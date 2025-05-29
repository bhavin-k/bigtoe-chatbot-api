from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    user_query: str
    provider_id: str

class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

class InitialMessageRequest(BaseModel):
    provider_id: str

class InitialMessageResponse(BaseModel):
    message: str
    success: bool
    error: Optional[str] = None