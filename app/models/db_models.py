import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    """users table"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_name = Column(String, unique=True)
    password = Column(String)
    name = Column(String)
    sessions_count = Column(Integer, default=0)

    # One-to-many: User -> ChatSessions
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    """Stores each user's chat session."""
    __tablename__ = "chat_sessions"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_session_name"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, nullable=False)  # User-entered session name
    created_at = Column(DateTime, default=datetime.utcnow)
    prompts_count = Column(Integer, default=0)

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Stores individual messages within a chat session."""
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String)  # 'user', 'assistant', etc.
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
