import json
import redis
from langchain.schema import AIMessage, HumanMessage
from typing import List, Union

class RedisManager:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """Initializes a Redis client connection."""
        self.client = redis.Redis(host=host, port=port, db=db)

    def get_session_key(self, session_id: str) -> str:
        """Generates a Redis key for a given chat session."""
        return f"session:{session_id}:history"

    def serialize_message(self, message: Union[AIMessage, HumanMessage]) -> str:
        """Converts a HumanMessage or AIMessage object into a JSON string."""
        return json.dumps({
            "type": "user" if isinstance(message, HumanMessage) else "ai",
            "content": message.content
        })
    
    def deserialize_message(self, raw: bytes) -> Union[AIMessage, HumanMessage]:
        """Converts a JSON string (from Redis) back into an AIMessage or HumanMessage."""
        data = json.loads(raw.decode("utf-8"))  # BUG FIX: Was using json.dumps instead of loads
        return AIMessage(data["content"]) if data["type"] == "ai" else HumanMessage(data["content"])
    
    def save_message(self, session_id: str, message: Union[AIMessage, HumanMessage]) -> None:
        """Saves a message to Redis for the given session. Keeps only the last 20 messages."""
        redis_key = self.get_session_key(session_id=session_id)
        self.client.rpush(redis_key, self.serialize_message(message=message))
        self.client.ltrim(redis_key, -20, -1)  # Keep only last 20 messages

    def session_exists(self, session_id: str) -> bool:
        """Checks if a Redis session exists for the given session ID."""
        return self.client.exists(self.get_session_key(session_id=session_id)) > 0
    
    def get_session_history(self, session_id: str) -> List[Union[AIMessage, HumanMessage]]:
        """Fetches the last 20 messages from Redis for a given session."""
        if not self.session_exists(session_id=session_id):
            return []
        
        redis_key = self.get_session_key(session_id=session_id)
        raw_messages = self.client.lrange(redis_key, 0, -1)
        return [self.deserialize_message(msg) for msg in raw_messages]

    def get_all_session_keys(self) -> List[str]:
        """Returns all session keys from Redis."""
        keys = self.client.keys("session:*:history")  # BUG FIX: function call missing ()
        return [key.decode("utf-8") for key in keys]

    def clear_session(self, session_id: str) -> None:
        """Deletes a session's history from Redis."""
        redis_key = self.get_session_key(session_id=session_id)
        self.client.delete(redis_key)
