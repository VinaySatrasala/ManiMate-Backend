# chat_application.py
from app.services.db_manager import DatabaseManager
from app.services.redis_manager import RedisManager
from app.services.memory_manager import MemoryManager
from app.services.chat_service import ChatService
from app.services.sync_service import SyncService
from app.config.app_config import AppConfig, get_default_config
from app.utils.system_prompt import build_prompt

class ChatApplication:
    def __init__(self, config: AppConfig = None):
        self.config = config or get_default_config()
        self.db_manager = None
        self.redis_manager = None
        self.memory_manager = None
        self.chat_service = None
        self.sync_service = None
        self.system_prompt = build_prompt()
        
    def initialize(self):
        """Initialize all components"""
        # Initialize managers
        self.db_manager = DatabaseManager(self.config.database.postgres_url)
        self.redis_manager = RedisManager(
            host=self.config.redis.host,
            port=self.config.redis.port,
            db=self.config.redis.db
        )
        self.memory_manager = MemoryManager(self.db_manager, self.redis_manager)
        

        
        self.chat_service = ChatService(
            self.memory_manager, 
            self.system_prompt
        )
        

        

        
        print("Chat application initialized successfully!")
    
    def chat(self, session_id: str, user_input: str) -> str:
        """Send a message and get response"""
        if not self.chat_service:
            raise RuntimeError("Application not initialized. Call initialize() first.")
        
        return self.chat_service.chat(session_id, user_input)
    
    def get_history(self, session_id: str):
        """Get conversation history"""
        if not self.chat_service:
            raise RuntimeError("Application not initialized. Call initialize() first.")
        
        return self.chat_service.get_conversation_history(session_id)
    
    def clear_session(self, session_id: str):
        """Clear a conversation session"""
        if not self.chat_service:
            raise RuntimeError("Application not initialized. Call initialize() first.")
        
        self.chat_service.clear_conversation(session_id)
    
    def sync_now(self):
        """Trigger immediate sync"""
        if self.sync_service:
            self.sync_service.sync_now()
    
    def shutdown(self):
        """Shutdown the application"""
        if self.sync_service:
            self.sync_service.stop()
        print("Chat application shutdown complete!")
