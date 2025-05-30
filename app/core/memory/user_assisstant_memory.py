from app.core.memory.embedding import VietnameseSBERTEmbeddingFunction
import chromadb


client = chromadb.PersistentClient(path="data/chromadb")


embedding_function = VietnameseSBERTEmbeddingFunction()

def get_or_create_ua_collection():
    """
    Get or Create User and Assistant memory collection
    
    Returns:
        chromadb.Collection: The collection for user and assistant memory
    """
    user_collection = client.get_or_create_collection(
        name="user",
        embedding_function=embedding_function
    )
    assistant_collection = client.get_or_create_collection(
        name="assistant",
        embedding_function=embedding_function
    )

    return user_collection, assistant_collection

def store_user_assistant_memory(role : str, text: str):
    """
    Store user or assistant memory in the respective collection.
    
    Args:
        role (str): The role of the message ('user' or 'assistant').
        text (str): The text to store in the memory.
    """
    user_collection, assistant_collection = get_or_create_ua_collection()
    
    if role == "user":
        user_collection.add(
            documents=[text],
            ids=[str(len(user_collection.get()['ids']) + 1)]
        )
    elif role == "assistant":
        assistant_collection.add(
            documents=[text],
            ids=[str(len(assistant_collection.get()['ids']) + 1)]
        )
    else:
        raise ValueError("Role must be either 'user' or 'assistant'.")
    
def retrieve_user_assistant_memory(role: str, query : str, limit: int = 5):
    """
    Retrieve user or assistant memory based on a query.
    
    Args:
        role (str): The role of the memory to retrieve ('user' or 'assistant').
        query (str): The query to search for in the memory.
        limit (int): The maximum number of results to return.
        
    Returns:
        list: List of retrieved documents.
    """
    user_collection, assistant_collection = get_or_create_ua_collection()
    
    if role == "user":
        results = user_collection.query(
            query_texts=[query],
            n_results=limit
        )
    elif role == "assistant":
        results = assistant_collection.query(
            query_texts=[query],
            n_results=limit
        )
    else:
        raise ValueError("Role must be either 'user' or 'assistant'.")
    
    return results['documents']