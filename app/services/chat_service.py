import logging
from typing import List
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from app.services.memory_manager import MemoryManager
from app.core.llm_config import LangchainLLMConfig

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class ChatService:
    def __init__(self, memory_manager: MemoryManager, system_prompt: str):
        self.memory_manager = memory_manager
        self.system_prompt = system_prompt
        self.llm = LangchainLLMConfig().langchain_llm  # LLM initialization

    def chat(self, session_id: str, user_id: str, user_input: str) -> str:
        """
        Handles a chat interaction:
        - Loads history from Redis or DB
        - Sends it to the LLM with system prompt
        - Saves both user and AI messages to memory
        """
        logger.info(f"Received user input for session '{session_id}' (user: {user_id})")

        # Step 1: Load past history
        history = self.memory_manager.load_history(session_id=session_id, user_id=user_id)

        # Step 2: Construct message chain
        messages = [SystemMessage(content=self.system_prompt)]
        messages.extend(history)
        messages.append(HumanMessage(content=user_input))

        # Step 3: Call LLM
        logger.info(f"Invoking LLM for session '{session_id}'")
        response_message = self.llm.invoke(messages)

        # Step 4: Save messages
        self.memory_manager.save_message(session_id=session_id, user_id=user_id, role="user", content=user_input)
        self.memory_manager.save_message(session_id=session_id, user_id=user_id, role="ai", content=response_message.content)

        logger.info(f"AI response saved for session '{session_id}'")
        return response_message.content

    def get_conversation_history(self, session_id: str, user_id: str) -> List:
        """
        Returns full reconstructed conversation history from memory.
        """
        logger.info(f"Fetching history for session '{session_id}'")
        return self.memory_manager.load_history(session_id=session_id, user_id=user_id)

    def clear_conversation_history(self, session_id: str, user_id: str) -> None:
        """
        Clears Redis + Postgres history for a given session.
        """
        logger.warning(f"Clearing history for session '{session_id}' (user: {user_id})")
        self.memory_manager.clear_session(session_id=session_id, user_id=user_id)

    def update_system_prompt(self, new_prompt: str) -> None:
        """Update the system prompt used for LLM interactions"""
        logger.info("System prompt updated")
        self.system_prompt = new_prompt
