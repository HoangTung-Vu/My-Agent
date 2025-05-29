from langchain_core.tools import Tool
import chromadb
from chromadb.utils import embedding_functions
from app.utils.pdf_process import db_dir_path, collection_name

collection_name = "pdf_collection"



client = chromadb.PersistentClient(path=str(db_dir_path))
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name=collection_name,
    embedding_function=embedding_function
)

def retrieve_documents(query: str, top_k: int = 5) -> str:
    """
    Retrieve documents from the ChromaDB collection based on a query.
    
    Args:
        query (str): The search query to find relevant documents.
        top_k (int): The number of top results to return.
        
    Returns:
        String containing the formatted results.
    """
    results = collection.query(query_texts=[query], n_results=top_k)
    
    if not results["documents"] or len(results["documents"][0]) == 0:
        return "No documents found matching the query."
    
    formatted_results = ""
    for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        source = metadata.get("source", "Unknown source")
        formatted_results += f"Document {i+1} (Source: {source}):\n{doc}\n\n"
    
    return formatted_results

# Create a Tool for LangChain
doc_retriever = Tool(
    name="doc_retriever",
    description="Retrieve relevant information from stored documents based on a query",
    func=retrieve_documents,
)
