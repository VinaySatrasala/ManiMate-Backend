import uuid
import logging
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.db_models import Base, ChatSession, ChatMessage, User

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
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
        return self.SessionLocal()
    
    def create_user(self, user_data) -> dict:
        db = self.get_session()
        try:
            new_user = User(
                id=str(uuid.uuid4()),
                user_name=user_data.user_name,
                password=user_data.password,
                name=user_data.name
            )
            db.add(new_user)
            db.commit()

            return {
                "id": new_user.id,
                "user_name": new_user.user_name,
                "name": new_user.name
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise
        finally:
            db.close()

    
    def user_exists(self,user_name) -> bool:
        db = self.get_session()
        try:
            user = db.query(User).filter_by(user_name=user_name).first()
            return user is not None
        except Exception as e:
            logger.error(f"Error checking user existence: {e}")
            raise
    
    def get_password_hash(self, user_name: str) -> Optional[str]:
        """Retrieve the hashed password for a user by username"""
        db = self.get_session()
        try:
            user = db.query(User).filter_by(user_name=user_name).first()
            if not user:
                logger.warning(f"User {user_name} not found")
                return None
            return user.password
        except Exception as e:
            logger.error(f"Error retrieving password hash for {user_name}: {e}")
            raise
        finally:
            db.close()
        

    def create_session(self, session_name: str, user_id: str) -> ChatSession:
        """Create a new chat session for a user (max 10 sessions allowed)"""
        db = self.get_session()
        try:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                raise ValueError(f"User with ID {user_id} does not exist.")

            if user.sessions_count >= 10:
                raise Exception("Maximum session limit (10) reached for this user.")

            session = ChatSession(id=str(uuid.uuid4()), name = session_name,user_id=user_id)
            db.add(session)
            user.sessions_count += 1
            db.commit()

            logger.info(f"Created chat session {session_name} for user {user_id}")
            return {
                "id": session.id,
                "name": session.name,
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat(),
                "prompts_count": session.prompts_count
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create chat session {session_name}: {e}")
            raise
        finally:
            db.close()

    def verify_session_ownership(self, db: Session, session_id: str, user_id: str) -> Optional[ChatSession]:
        """Helper: fetch session only if it belongs to the given user"""
        session = db.query(ChatSession).filter_by(id=session_id, user_id=user_id).first()
        if not session:
            raise ValueError(f"Session {session_id} does not belong to user {user_id}")
        return session

    def get_chat_session(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        """Fetch a chat session by ID, only if owned by the user"""
        db = self.get_session()
        try:
            return self.verify_session_ownership(db, session_id, user_id)
        except Exception as e:
            logger.error(f"Error retrieving session {session_id} for user {user_id}: {e}")
            raise
        finally:
            db.close()
    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        """Retrieve all chat sessions for a user"""
        db = self.get_session()
        try:
            sessions = db.query(ChatSession).filter_by(user_id=user_id).all()
            if not sessions:
                logger.warning(f"No sessions found for user {user_id}")
            return sessions
        except Exception as e:
            logger.error(f"Error fetching sessions for user {user_id}: {e}")
            raise
        finally:
            db.close()
    
    def save_message(self, session_id: str, user_id: str, role: str, content: str) -> ChatMessage:
        """Save a message to a session, verifying ownership and prompt limit"""
        db = self.get_session()
        try:
            session = self.verify_session_ownership(db, session_id, user_id)

            if session.prompts_count >= 20:
                raise Exception(f"Session {session_id} has reached the max prompt limit (20)")

            message = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role=role,
                content=content,
            )
            db.add(message)
            session.prompts_count += 1
            db.commit()

            logger.info(f"Saved message to session {session_id} for user {user_id}")
            return message
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save message for session {session_id}, user {user_id}: {e}")
            raise
        finally:
            db.close()

    def get_session_messages(self, session_id: str, user_id: str) -> List[ChatMessage]:
        """Retrieve all messages for a session, only if owned by the user"""
        db = self.get_session()
        try:
            self.verify_session_ownership(db, session_id, user_id)
            return db.query(ChatMessage).filter_by(session_id=session_id).all()
        except Exception as e:
            logger.error(f"Error fetching messages for session {session_id}, user {user_id}: {e}")
            raise
        finally:
            db.close()

    def delete_session(self, session_id: str, user_id: str):
        """Delete all messages for a session (verifying ownership)"""
        db = self.get_session()
        try:
            self.verify_session_ownership(db, session_id, user_id)
            session_obj = db.query(ChatSession).filter_by(id=session_id).first()
            if session_obj:
                db.delete(session_obj)
                db.commit()

            logger.info(f"Deleted {session_obj} messages for session {session_id} (user {user_id})")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete messages for session {session_id}, user {user_id}: {e}")
            raise
        finally:
            db.close()
