from app.services.db_manager import DatabaseManager
from app.services.redis_manager import RedisManager
from typing import List, Union
from langchain.schema import AIMessage, HumanMessage

class MemoryManager:
    def __init__(self, database_manager: DatabaseManager, redis_manager: RedisManager):
        """Initializes the memory manager with both database and Redis interfaces."""
        self.database_manager = database_manager
        self.redis_manager = redis_manager

    def load_history(self, session_id: str) -> List[Union[AIMessage, HumanMessage]]:
        """
        Loads chat history for a session.
        - Tries Redis first (fast).
        - Falls back to DB if not found, and then backfills Redis.
        """
        history = self.redis_manager.get_session_history(session_id=session_id)
        if history:
            return history

        messages = self.database_manager.get_session_messages(session_id=session_id)
        history = []

        for message in messages:
            temp = HumanMessage(content=message.content) if message.role == "user" else AIMessage(content=message.content)
            history.append(temp)
            self.redis_manager.save_message(session_id=session_id, message=temp)  # FIXED: was passing DB message object

        return history

    def save_message(self, session_id: str, role: str, content: str) -> None:
        """
        Saves a single chat message to both Redis and the database.
        """
        message = HumanMessage(content=content) if role == "user" else AIMessage(content=content)
        self.redis_manager.save_message(session_id=session_id, message=message)  # FIXED: was missing session_id
        self.database_manager.save_message(session_id=session_id, role=role, content=content)

    def sync_redis_to_postgres(self) -> None:
        """
        Syncs all chat sessions from Redis to PostgreSQL.
        - Assumes Redis has source of truth for recent state.
        - Rewrites session in DB.
        """
        session_keys = self.redis_manager.get_all_session_keys()

        for key in session_keys:
            try:
                session_id = key.split(":")[1]
                messages = self.redis_manager.get_session_history(session_id=session_id)
                if not messages:
                    continue

                # Ensure DB session exists
                session_exists = self.database_manager.get_chat_session(session_id=session_id)

                if not session_exists:
                    self.database_manager.create_session(session_id=session_id, user_id=session_id)
                else:
                    self.database_manager.delete_session_messages(session_id=session_id)


                # Clear old messages from DB
                self.database_manager.delete_session_messages(session_id=session_id)

                for msg in messages:
                    role = "user" if isinstance(msg, HumanMessage) else "ai"  # FIXED: isinstance(msg), not isinstance(HumanMessage)
                    self.database_manager.save_message(session_id=session_id, role=role, content=msg.content)

                print(f"[✓] Synced session {session_id} from Redis to DB.")

            except Exception as e:
                print(f"[✗] Error syncing session {session_id}: {e}")

        print("✅ Redis to DB sync completed.")

    def clear_session(self, session_id: str) -> None:
        """
        Clears session data from both Redis and PostgreSQL.
        """
        self.redis_manager.clear_session(session_id=session_id)
        self.database_manager.delete_session_messages(session_id=session_id)
