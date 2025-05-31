from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.memory.summary_buffer import ConversationSummaryBufferMemory

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.chat_history import BaseChatMessageHistory

def get_chat_history(session_id : str):
    history = SQLChatMessageHistory(
        table_name='messages',
        session_id=session_id,
        connection="sqlite:///./data/database.db"
    )

    return history

def get_memory(llm : BaseLanguageModel, chat_memory : BaseChatMessageHistory):
    return ConversationSummaryBufferMemory(
        llm=llm,
        chat_memory=chat_memory,
        max_token_limit=500000, 
    )

def get_recent_chat_history(session_id : str, number_of_messages : int = 5):
    """
    Get recent chat history for a specific session. Query sqlite directly and add message to List[BaseMessage]
    Args:
        session_id (str): The ID of the session to retrieve history for.
        number_of_messages (int): The number of recent messages to retrieve.
    Returns:
        List[BaseMessage]: List of recent chat messages as BaseMessage objects.
    """
    import sqlite3
    from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

    db_path = './data/database.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Giả sử bảng messages có các trường: id, session_id, role, content, created_at
    query = '''
        SELECT role, content FROM messages
        WHERE session_id = ?
        ORDER BY timestamp DESC, id DESC
        LIMIT ?
    '''
    cursor.execute(query, (session_id, number_of_messages))
    rows = cursor.fetchall()
    conn.close()

    rows = rows[::-1]
    messages = []
    for role, content in rows:
        if role == 'assistant':
            messages.append(AIMessage(content=content))
        elif role == 'user':
            messages.append(HumanMessage(content=content))
    return messages
