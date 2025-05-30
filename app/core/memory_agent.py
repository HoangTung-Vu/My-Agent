from app.core import memory 
from app.core.llm import llm
from typing import List, Dict, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate


class MemoryAgent : 
    def __init__(self) : 
        self.llm = llm
    
    def decide_store(self, recent_chat_history : List[BaseMessage]) -> Optional[Dict[str, str]]:
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
            ("system", "You are a memory agent. Based on the following chat history, decide if there is any important information about the user or assistant that should be stored in long-term memory. If so, briefly summarize the information to be stored for each role. Return only lines starting with 'user:' and/or 'assistant:' if there is information to store. If there is nothing to store, return an empty string for that role.\nChat history :\n{history}"),
        ])

        history_text = "\n".join([
            f"User: {msg.content}" if msg.type == 'human' else f"Assistant: {msg.content}" for msg in recent_chat_history
        ])
        messages = prompt.format(history=history_text)
        response = self.llm.invoke(messages)
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
