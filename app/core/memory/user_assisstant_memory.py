import asyncio
from app.core.memory.embedding import VietnameseSBERTEmbeddingFunction
import chromadb
import uuid # Import uuid


client = chromadb.PersistentClient(path="data/chromadb")


embedding_function = VietnameseSBERTEmbeddingFunction()

async def get_or_create_ua_collection():
    """
    Get or Create User and Assistant memory collection asynchronously.
    
    Returns:
        tuple[chromadb.Collection, chromadb.Collection]: The user and assistant collections.
    """
    # Run synchronous chromadb client calls in a separate thread
    user_collection = await asyncio.to_thread(
        client.get_or_create_collection,
        name="user",
        embedding_function=embedding_function
    )
    assistant_collection = await asyncio.to_thread(
        client.get_or_create_collection,
        name="assistant",
        embedding_function=embedding_function
    )
    return user_collection, assistant_collection

async def store_user_assistant_memory(role : str, text: str):
    """
    Store user or assistant memory in the respective collection asynchronously.
    
    Args:
        role (str): The role of the message ('user' or 'assistant').
        text (str): The text to store in the memory.
    """
    user_collection, assistant_collection = await get_or_create_ua_collection()
    
    collection_to_use = None
    if role == "user":
        collection_to_use = user_collection
    elif role == "assistant":
        collection_to_use = assistant_collection
    else:
        raise ValueError("Role must be either 'user' or 'assistant'.")

    if collection_to_use:
        new_id = str(uuid.uuid4()) # Use uuid for new_id
        
        await asyncio.to_thread(
            collection_to_use.add,
            documents=[text],
            ids=[new_id]
        )
    
async def retrieve_user_assistant_memory(role: str, query : str, limit: int = 5):
    """
    Retrieve user or assistant memory based on a query asynchronously.
    
    Args:
        role (str): The role of the memory to retrieve ('user' or 'assistant').
        query (str): The query to search for in the memory.
        limit (int): The maximum number of results to return.
        
    Returns:
        list: List of retrieved documents.
    """
    user_collection, assistant_collection = await get_or_create_ua_collection()
    
    collection_to_query = None
    if role == "user":
        collection_to_query = user_collection
    elif role == "assistant":
        collection_to_query = assistant_collection
    else:
        raise ValueError("Role must be either 'user' or 'assistant'.")

    if collection_to_query:
        results = await asyncio.to_thread(
            collection_to_query.query,
            query_texts=[query],
            n_results=limit
        )
        return results['documents']
    return []