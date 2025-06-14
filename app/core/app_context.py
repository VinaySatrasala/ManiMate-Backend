# app/core/context.py
from app.core.chat_application import ChatApplication
from app.services.db_manager import DatabaseManager
from app.services.redis_manager import RedisManager
from app.services.memory_manager import MemoryManager
from app.services.chat_service import ChatService
from app.config.app_config import get_default_config
from app.services.sync_service import SyncService
from app.utils.system_prompt import build_prompt


class AppContext:
    def __init__(self):
        self.config = get_default_config()

        self.db_manager = DatabaseManager(self.config.database.postgres_url)

        self.redis_manager = RedisManager(
            host=self.config.redis.host,
            port=self.config.redis.port,
            db=self.config.redis.db
        )

        self.memory_manager = MemoryManager(
            self.db_manager, self.redis_manager)

        self.chat_service = ChatService(
            memory_manger=self.memory_manager,
            system_prompt=self.system_prompt
        )
        self.sync_service = SyncService(
            memory_manager=self.memory_manager
        )
        self.chat_application = ChatApplication(
            db_manager=self.db_manager,
            redis_manager=self.redis_manager,
            memory_manager=self.memory_manager,
            chat_service=self.chat_service,
            sync_service=self.sync_service
        )
        
        self.system_prompt = build_prompt()


# Create a shared instance
app_context = AppContext()
