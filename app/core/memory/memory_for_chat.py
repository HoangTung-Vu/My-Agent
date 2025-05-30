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

def get_recent_chat_history(conversation_id : str, number_of_messages : int = 5):
    """
    Get recent chat history for a specific conversation. Query sqlite directly and add message to List[BaseMessage]
    Args:
        conversation_id (str): The ID of the conversation to retrieve history for.
        number_of_messages (int): The number of recent messages to retrieve.
    Returns:
        List[BaseMessage]: List of recent chat messages as BaseMessage objects.
    """
    import sqlite3
    from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

    db_path = './data/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Giả sử bảng messages có các trường: id, conversation_id, role, content, created_at
    query = '''
        SELECT role, content FROM messages
        WHERE conversation_id = ?
        ORDER BY timestamp DESC, id DESC
        LIMIT ?
    '''
    cursor.execute(query, (conversation_id, number_of_messages))
    rows = cursor.fetchall()
    conn.close()

    # Đảo ngược lại để đúng thứ tự thời gian
    rows = rows[::-1]
    messages = []
    for role, content in rows:
        if role == 'assistant':
            messages.append(AIMessage(content=content))
        elif role == 'user':
            messages.append(HumanMessage(content=content))
        # Có thể mở rộng cho các role khác nếu cần
    return messages
