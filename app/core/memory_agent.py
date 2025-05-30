from app.core import memory 
from app.core.llm import llm
from typing import List, Dict, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path # Add Path import

SCRIPT_DIR = Path(__file__).parent.resolve()
with open(SCRIPT_DIR / "system_prompt_collection/decide_store_memory_agent.txt", "r") as f:
    DECIDE_STORE_SYSTEM_PROMPT = f.read().strip()

with open(SCRIPT_DIR / "system_prompt_collection/decide_query_memory_agent.txt", "r") as f:
    DECIDE_QUERY_SYSTEM_PROMPT = f.read().strip()

class MemoryAgent : 
    def __init__(self) : 
        self.llm = llm
    
    async def decide_store(self, recent_chat_history : List[BaseMessage]) -> Optional[Dict[str, str]]:
        """
        Decide whether to store information about the user and assistant base on recent chat history
        If there is no information need to store return None 
        If there is information need to store return a dict with keys "user" and "assistant" and their corresponding helpful information
        Arg : 
            recent_chat_history (List[BaseMessage]): List of recent chat messages as BaseMessage objects.
        Returns:
            Optional[Dict[str, str]]: A dictionary with keys "user" and/or "assistant" if there is information to store, otherwise None.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", DECIDE_STORE_SYSTEM_PROMPT + "\nChat history :\n{history}"),
        ])

        history_text = "\n".join([
            f"User: {msg.content}" if msg.type == 'human' else f"Assistant: {msg.content}" for msg in recent_chat_history
        ])
        messages = prompt.format(history=history_text)
        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        result = {}
        for line in content.splitlines():
            if line.lower().startswith('user:'):
                value = line.split(':',1)[1].strip()
                if value:
                    result['user'] = value
            elif line.lower().startswith('assistant:'):
                value = line.split(':',1)[1].strip()
                if value:
                    result['assistant'] = value
        if not result:
            return None
        return result

    async def decide_query(self, input_message : str, recent_chat_history : List[BaseMessage]) -> Optional[Dict[str,str]]:
        """
        Decide what to query from the user and assistant memory based on the input message and recent chat history.
        If there is no information to query, return None.
        Args:
            input_message (str): The input message from the user.
            recent_chat_history (List[BaseMessage]): List of recent chat messages as BaseMessage objects.
        Returns:
            Optional[str]: A query string if there is information to query in which memory (user/ assistant), otherwise None.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", DECIDE_QUERY_SYSTEM_PROMPT + "\nInput message: {input_message}\nRecent chat history:\n{history}"),
        ])

        history_text = "\n".join([
            f"User: {msg.content}" if msg.type == 'human' else f"Assistant: {msg.content}" for msg in recent_chat_history
        ])
        messages = prompt.format(input_message=input_message, history=history_text)
        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        result = {}
        for line in content.splitlines():
            if line.lower().startswith('user:'):
                value = line.split(':',1)[1].strip()
                if value:
                    result['user'] = value
            elif line.lower().startswith('assistant:'):
                value = line.split(':',1)[1].strip()
                if value:
                    result['assistant'] = value
        if not result:
            return None
        return result