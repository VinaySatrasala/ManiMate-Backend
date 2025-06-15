import json
import redis
from typing import List, Union
from langchain.schema import AIMessage, HumanMessage
from app.services.db_manager import DatabaseManager  # import your DB manager

class RedisManager:
    def __init__(self, db_manager: DatabaseManager, host: str = "localhost", port: int = 6379, db: int = 0):
        """Initializes Redis and Database managers."""
        self.client = redis.Redis(host=host, port=port, db=db)
        self.db_manager = db_manager

    def get_session_key(self, session_id: str, user_id: str) -> str:
        """Generates a Redis key based on user and session for isolation and ownership."""
        return f"user:{user_id}:session:{session_id}:history"

    def serialize_message(self, message: Union[AIMessage, HumanMessage]) -> str:
        """Converts a HumanMessage or AIMessage to JSON."""
        return json.dumps({
            "type": "human" if isinstance(message, HumanMessage) else "ai",
            "content": message.content
        })

    def deserialize_message(self, raw: bytes) -> Union[AIMessage, HumanMessage]:
        """Deserializes Redis-stored JSON back into a Langchain Message."""
        data = json.loads(raw.decode("utf-8"))
        return AIMessage(data["content"]) if data["type"] == "ai" else HumanMessage(data["content"])

    def save_message(self, session_id: str, user_id: str, message: Union[AIMessage, HumanMessage]) -> None:
        """Saves a message to Redis after validating DB session ownership."""
        # Ownership check + prompt limit enforcement
        session = self.db_manager.get_chat_session(session_id=session_id, user_id=user_id)
        if session.prompts_count >= 20:
            raise Exception(f"Prompt limit reached for session {session_id}.")

        # Save to Redis
        redis_key = self.get_session_key(session_id, user_id)
        self.client.rpush(redis_key, self.serialize_message(message))
        self.client.ltrim(redis_key, -20, -1)  # Keep only last 20 messages

        # Save to DB
        # self.db_manager.save_message(session_id=session_id, user_id=user_id, role=message.type, content=message.content)

    def session_exists(self, session_id: str, user_id: str) -> bool:
        """Check if a Redis history exists for this user’s session."""
        return self.client.exists(self.get_session_key(session_id, user_id)) > 0

    def get_session_history(self, session_id: str, user_id: str) -> List[Union[AIMessage, HumanMessage]]:
        """Retrieve last 20 messages from Redis after ownership verification."""
        # Ownership validation
        self.db_manager.get_chat_session(session_id=session_id, user_id=user_id)

        if not self.session_exists(session_id, user_id):
            return []

        redis_key = self.get_session_key(session_id, user_id)
        raw_messages = self.client.lrange(redis_key, 0, -1)
        return [self.deserialize_message(msg) for msg in raw_messages]

    def get_all_session_keys(self, user_id: str) -> List[str]:
        """Returns all session keys for the current user."""
        keys = self.client.keys(f"user:{user_id}:session:*:history")
        return [key.decode("utf-8") for key in keys]

    def clear_session(self, session_id: str, user_id: str) -> None:
        """Deletes Redis chat history for a user’s session."""
        redis_key = self.get_session_key(session_id, user_id)
        self.client.delete(redis_key)
