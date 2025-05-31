from typing import Dict, Optional
from app.models.schema import Chat, ChatMessage
import uuid
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

class ChatManager:
    def __init__(self):
        self.chats: Dict[str, Chat] = {}
        self.memories: Dict[str, ConversationBufferMemory] = {}

    def create_chat(self) -> str:
        chat_id = str(uuid.uuid4())
        self.chats[chat_id] = Chat(
            id=chat_id,
            messages=[],
            title="New Chat"
        )
        self.memories[chat_id] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        return chat_id

    def get_chat(self, chat_id: str) -> Optional[Chat]:
        return self.chats.get(chat_id)

    def add_message(self, chat_id: str, role: str, content: str):
        if chat_id not in self.chats:
            chat_id = self.create_chat()

        chat = self.chats[chat_id]
        chat.messages.append(ChatMessage(role=role, content=content))
        
        # Update memory
        memory = self.memories[chat_id]
        if role == "human":
            memory.chat_memory.add_message(HumanMessage(content=content))
        elif role == "ai":
            memory.chat_memory.add_message(AIMessage(content=content))

    def get_memory(self, chat_id: str) -> Optional[ConversationBufferMemory]:
        return self.memories.get(chat_id)

    def list_chats(self):
        return [{"id": chat.id, "title": chat.title} for chat in self.chats.values()]