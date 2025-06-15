from typing import List, Union
from langchain.schema import AIMessage, HumanMessage
from app.services.db_manager import DatabaseManager
from app.services.redis_manager import RedisManager

class MemoryManager:
    def __init__(self, database_manager: DatabaseManager, redis_manager: RedisManager):
        """Initializes the memory manager with both database and Redis interfaces."""
        self.database_manager = database_manager
        self.redis_manager = redis_manager

    def load_history(self, session_id: str, user_id: str) -> List[Union[AIMessage, HumanMessage]]:
        """
        Loads chat history for a session.
        - Tries Redis first (fast).
        - Falls back to DB if not found, and then backfills Redis.
        """
        history = self.redis_manager.get_session_history(session_id=session_id, user_id=user_id)
        if history:
            return history

        messages = self.database_manager.get_session_messages(session_id=session_id, user_id=user_id)
        history = []

        for message in messages:
            temp = HumanMessage(content=message.content) if message.role == "human" else AIMessage(content=message.content)
            history.append(temp)
            self.redis_manager.save_message(session_id=session_id, user_id=user_id, message=temp)

        return history

    def save_message(self, session_id: str, user_id: str, role: str, content: str) -> None:
        """
        Saves a single chat message to both Redis and the database.
        """
        message = HumanMessage(content=content) if role == "human" else AIMessage(content=content)
        self.redis_manager.save_message(session_id=session_id, user_id=user_id, message=message)
        self.database_manager.save_message(session_id=session_id, user_id=user_id, role=role, content=content)

    def sync_redis_to_postgres(self) -> None:
        """
        Syncs all chat sessions from Redis to PostgreSQL.
        - Redis is assumed to be the latest source of truth.
        """
        session_keys = self.redis_manager.get_all_session_keys()

        for key in session_keys:
            try:
                # Key format: user:{user_id}:session:{session_id}:history
                parts = key.split(":")
                user_id = parts[1]
                session_id = parts[3]

                messages = self.redis_manager.get_session_history(session_id=session_id, user_id=user_id)
                if not messages:
                    continue

                session_exists = self.database_manager.get_chat_session(session_id=session_id, user_id=user_id)
                if not session_exists:
                    self.database_manager.create_session(session_id=session_id, user_id=user_id)
                else:
                    self.database_manager.delete_session_messages(session_id=session_id, user_id=user_id)

                for msg in messages:
                    role = "human" if isinstance(msg, HumanMessage) else "ai"
                    self.database_manager.save_message(session_id=session_id, user_id=user_id, role=role, content=msg.content)

                print(f"[✓] Synced session {session_id} for user {user_id} from Redis to DB.")
            except Exception as e:
                print(f"[✗] Error syncing session {session_id} for user {user_id}: {e}")

        print("✅ Redis to DB sync completed.")

    def clear_session(self, session_id: str, user_id: str) -> None:
        """
        Clears session data from both Redis and PostgreSQL.
        """
        self.redis_manager.clear_session(session_id=session_id, user_id=user_id)
        self.database_manager.delete_session_messages(session_id=session_id, user_id=user_id)
