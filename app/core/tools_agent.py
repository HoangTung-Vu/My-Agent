from app.core import tools
from app.core.tools import all_tools
from app.core.llm import tools_llm
from langchain_core.messages import AIMessage, ToolMessage, BaseMessage, HumanMessage
from typing import List, Optional, Dict, Any, Tuple, Union


class ToolsAgent : 
    def __init__(self) : 
        self.llm_with_tools = tools_llm.bind_tools(list(all_tools.values()))
        self.tools_map = all_tools
    
    def select_tool(self, query: str, recent_chat_history : List[BaseMessage]):
        messages : List[BaseMessage] = list(recent_chat_history)
        messages.append(HumanMessage(content=query))
        response = self.llm_with_tools.invoke(messages)
        
        return response.content, response.tool_calls
    
    def run_tool(self, tool_call: Dict[str, Any]):
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get("id", "tool_call_id_not_provided")
        tool = self.tools_map.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found.")
        try:
            result = tool.invoke(tool_args)
            return ToolMessage(
                content=result,
                name=tool_name,
                tool_call_id=tool_call_id
            )
        except Exception as e:
            return ToolMessage(
                content=f"Error running tool '{tool_name}': {str(e)}",
                name=tool_name,
                tool_call_id=tool_call_id
            )