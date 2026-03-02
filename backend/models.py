from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChatRequest(BaseModel):
    messages: List[Dict[str, str]] 
    thread_id: str = Field(default="default_thread", description="Unique ID for conversation memory")


class ChatResponse(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None





