import uuid
import logging
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.db_models import Base, ChatSession, ChatMessage

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # or DEBUG for more detail
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class DatabaseManager:
    def __init__(self, postgres_url: str):
        self.engine = create_engine(postgres_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def create_session(self, session_id: str, user_id: str) -> ChatSession:
        """Create a new chat session"""
        db = self.get_session()
        try:
            session = ChatSession(id=session_id, user_id=user_id)
            db.add(session)
            db.commit()
            logger.info(f"Created chat session: {session_id}")
            return session
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create chat session {session_id}: {e}")
            raise
        finally:
            db.close()
    
    def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Fetch a chat session by ID"""
        db = self.get_session()
        try:
            return db.query(ChatSession).filter_by(id=session_id).first()
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {e}")
            raise
        finally:
            db.close()
    
    def save_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        """Save a new message to a session"""
        db = self.get_session()
        try:
            session = db.query(ChatSession).filter_by(id=session_id).first()
            if not session:
                logger.warning(f"No session found for {session_id}, creating new one.")
                session = ChatSession(id=session_id, user_id=session_id)
                db.add(session)
                db.commit()
            
            message = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role=role,
                content=content,
            )
            db.add(message)
            db.commit()
            logger.info(f"Saved message to session {session_id}")
            return message
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save message for session {session_id}: {e}")
            raise
        finally:
            db.close()
    
    def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """Retrieve all messages for a given session"""
        db = self.get_session()
        try:
            return db.query(ChatMessage).filter_by(session_id=session_id).all()
        except Exception as e:
            logger.error(f"Error fetching messages for session {session_id}: {e}")
            raise
        finally:
            db.close()
    
    def delete_session_messages(self, session_id: str):
        """Delete all messages for a given session"""
        db = self.get_session()
        try:
            deleted = db.query(ChatMessage).filter_by(session_id=session_id).delete()
            db.commit()
            logger.info(f"Deleted {deleted} messages for session {session_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete messages for session {session_id}: {e}")
            raise
        finally:
            db.close()
