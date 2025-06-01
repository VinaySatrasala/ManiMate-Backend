from app.services.memory_manager import MemoryManager
from app.core.llm_config import LangchainLLMConfig
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from typing import List


class ChatService:
    def __init__(self, memory_manger: MemoryManager, system_prompt: str):
        self.memory_manager = memory_manger
        self.system_prompt = system_prompt
        self.llm = LangchainLLMConfig().langchain_llm  # Initializes the LLM client

    def chat(self, session_id: str, user_input: str) -> str:
        """
        Handles a chat interaction:
        - Loads past messages from Redis or DB
        - Constructs the full message history including system prompt
        - Sends it to the LLM and gets the response
        - Saves both user and AI messages to memory
        - Returns the AI response
        """
        history = self.memory_manager.load_history(session_id=session_id)

        # Inject system prompt
        messages = [SystemMessage(content=self.system_prompt)]
        messages.extend(history)
        messages.append(HumanMessage(content=user_input))

        response_message = self.llm.invoke(messages)

        # Save messages in both Redis and DB
        self.memory_manager.save_message(
            session_id=session_id, role="user", content=user_input)
        self.memory_manager.save_message(
            session_id=session_id, role="ai", content=response_message.content)

        return response_message

    def get_conversation_history(self, session_id: str) -> List:
        """
        Returns full reconstructed conversation history from memory.
        """
        return self.memory_manager.load_history(session_id=session_id)

    def clear_conversation_history(self, session_id: str) -> None:
        """
        Clears Redis + Postgres history for a given session.
        """
        self.memory_manager.clear_session(session_id=session_id)

    def update_system_prompt(self, new_prompt: str) -> None:
        """Update the system prompt"""
        self.system_prompt = new_prompt
