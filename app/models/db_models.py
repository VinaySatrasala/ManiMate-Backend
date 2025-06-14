from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """users table"""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    user_name = Column(String)
    password = Column(String)
    name = Column(String)
    sessions_count = Column(Integer, default=0)  # Track number of sessions

    # One-to-many: User -> ChatSessions
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    """Stores each user's chat session."""
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    prompts_count = Column(Integer, default=0)  # Track number of prompts per session

    # Many-to-one: Session -> User
    user = relationship("User", back_populates="sessions")

    # One-to-many: Session -> Messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Stores individual messages within a chat session."""
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"))
    role = Column(String)  # 'user', 'assistant', etc.
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Many-to-one: Message -> Session
    session = relationship("ChatSession", back_populates="messages")
