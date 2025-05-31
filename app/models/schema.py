from pydantic import BaseModel
from typing import Optional, List, Dict

class PromptSchema(BaseModel):
    prompt: str
    chat_id: Optional[str] = None

class VideoSchema(BaseModel):
    filename: str

class ChatMessage(BaseModel):
    role: str
    content: str

class Chat(BaseModel):
    id: str
    messages: List[ChatMessage]
    title: Optional[str] = None

class ChatResponse(BaseModel):
    chat_id: str
    response: str
    messages: List[Dict[str, str]]