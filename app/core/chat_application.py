from app.services.db_manager import DatabaseManager
from app.services.redis_manager import RedisManager
from app.services.memory_manager import MemoryManager
from app.services.chat_service import ChatService
from app.services.sync_service import SyncService
from app.utils.system_prompt import build_prompt
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class ChatApplication:
    def __init__(self,
                 db_manager: DatabaseManager,
                 redis_manager: RedisManager,
                 memory_manager: MemoryManager,
                 chat_service: ChatService,
                 sync_service: SyncService
                 ):
        self.db_manager = db_manager
        self.redis_manager = redis_manager
        self.memory_manager = memory_manager
        self.chat_service = chat_service
        self.sync_service = sync_service
        self.system_prompt = build_prompt()

    # def initialize(self):
    #     """Initialize all components"""
    #     self.db_manager = DatabaseManager(self.config.database.postgres_url)
    #     self.redis_manager = RedisManager(
    #         host=self.config.redis.host,
    #         port=self.config.redis.port,
    #         db=self.config.redis.db
    #     )
    #     self.memory_manager = MemoryManager(self.db_manager, self.redis_manager)

    #     self.chat_service = ChatService(
    #         memory_manager=self.memory_manager,
    #         system_prompt=self.system_prompt
    #     )

    #     self.sync_service = SyncService(memory_manager=self.memory_manager)

    #     logger.info("✅ Chat application initialized successfully!")

    def chat(self, session_id: str, user_id: str, user_input: str) -> str:
        """Send a message and get response"""
        if not self.chat_service:
            raise RuntimeError(
                "Application not initialized. Call initialize() first.")

        return self.chat_service.chat(session_id=session_id, user_id=user_id, user_input=user_input)

    def get_history(self, session_id: str, user_id: str):
        """Get conversation history"""
        if not self.chat_service:
            raise RuntimeError(
                "Application not initialized. Call initialize() first.")

        return self.chat_service.get_conversation_history(session_id=session_id, user_id=user_id)

    def clear_session(self, session_id: str, user_id: str):
        """Clear a conversation session"""
        if not self.chat_service:
            raise RuntimeError(
                "Application not initialized. Call initialize() first.")

        self.chat_service.clear_conversation_history(
            session_id=session_id, user_id=user_id)

    def sync_now(self):
        """Trigger immediate sync"""
        if self.sync_service:
            self.sync_service.sync_now()

    def shutdown(self):
        """Shutdown the application"""
        if self.sync_service:
            self.sync_service.stop()
        logger.info("🛑 Chat application shutdown complete.")
