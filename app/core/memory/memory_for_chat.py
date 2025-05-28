# File này sẽ khai báo 1 ConversationSummaryBufferMemory để lưu trữ lịch sử hội thoại
# Trong file có các hàm để lấy lịch sử hội thoại từ sqlite và lưu lại vào memory object

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory.summary_buffer import ConversationSummaryBufferMemory

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.chat_history import BaseChatMessageHistory

def get_chat_history(conversation_id : str):
    return SQLChatMessageHistory(
        table_name="messages",
        connection_string="sqlite:///./data/database.db",
        session_id_field_name="conversation_id",
        session_id = conversation_id
    )

def get_memory(llm : BaseLanguageModel, chat_memory : BaseChatMessageHistory):
    return ConversationSummaryBufferMemory(
        llm=llm,
        chat_memory=chat_memory,
        max_token_limit=500000, 
    )