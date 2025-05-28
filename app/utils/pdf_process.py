import os
import PyPDF2
from pathlib import Path
from typing import List, Dict, Any, Tuple

import chromadb
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter


pdf_dir_path = Path("pdfs")
db_dir_path = Path("data/chromadb")
collection_name = "pdf_collection"
chunk_size = 1000
chunk_overlap = 200

# Create directories if they don't exist
os.makedirs(pdf_dir_path, exist_ok=True)
os.makedirs(db_dir_path, exist_ok=True)

# Initialize ChromaDB client and embedding function at the module level
client = chromadb.PersistentClient(path=str(db_dir_path))
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Create or get collection at the module level
collection = client.get_or_create_collection(
    name=collection_name,
    embedding_function=embedding_function
)

# Initialize text splitter for chunking at the module level
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap
)

def initialize_pdf_processor(
    pdf_dir: str = "pdfs",
    db_dir: str = "data/chromadb",
    collection_name: str = "pdf_collection",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> Tuple[chromadb.Collection, embedding_functions.SentenceTransformerEmbeddingFunction]:
    """
    Re-initialize the PDF processor components with new parameters
    
    Args:
        pdf_dir: Directory containing PDF files
        db_dir: Directory for ChromaDB storage
        collection_name: Name of the collection in ChromaDB
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        
    Returns:
        Tuple containing the collection and embedding function
    """
    global client, embedding_function, collection, text_splitter
    global pdf_dir_path, db_dir_path
    
    # Update paths
    pdf_dir_path = Path(pdf_dir)
    db_dir_path = Path(db_dir)
    
    # Create directories if they don't exist
    os.makedirs(pdf_dir_path, exist_ok=True)
    os.makedirs(db_dir_path, exist_ok=True)
    
    # Re-initialize client with new parameters
    client = chromadb.PersistentClient(path=str(db_dir_path))
    
    # No need to recreate the embedding function unless model changes
    
    # Create or get collection with new name
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )
    
    # Update text splitter with new parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    return collection, embedding_function

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def chunk_text(text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Split text into chunks."""
    chunks = text_splitter.split_text(text)
    documents = []
    
    for i, chunk in enumerate(chunks):
        doc = {
            "text": chunk,
            "metadata": {**metadata, "chunk_id": i}
        }
        documents.append(doc)
    
    return documents

def add_to_collection(documents: List[Dict[str, Any]]):
    """Add documents to ChromaDB collection."""
    if not documents:
        return
    
    ids = [f"{doc['metadata']['filename']}_{doc['metadata']['chunk_id']}" for doc in documents]
    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    # Add documents to collection
    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )
    
    print(f"Added {len(documents)} chunks to collection {collection_name}")

def process_pdf(pdf_path: Path):
    """Process a single PDF file."""
    print(f"Processing {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print(f"No text extracted from {pdf_path}")
        return
    
    metadata = {
        "filename": pdf_path.name,
        "source": str(pdf_path)
    }
    
    documents = chunk_text(text, metadata)
    add_to_collection(documents)

def process_all_pdfs(pdf_dir: str = None):
    """Process all PDFs in the directory."""
    dir_path = Path(pdf_dir) if pdf_dir else pdf_dir_path
    pdf_files = list(dir_path.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {dir_path}")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    for pdf_file in pdf_files:
        process_pdf(pdf_file)
    
    print(f"Total documents in collection: {collection.count()}")

def get_embedding_function():
    """Get the current embedding function."""
    return embedding_function

def process_pdfs(
    pdf_dir: str = None, 
    db_dir: str = None, 
    collection_name: str = None,
    chunk_size: int = None, 
    chunk_overlap: int = None
):
    """
    Process PDFs and add them to ChromaDB.
    
    Args:
        pdf_dir: Directory containing PDF files
        db_dir: Directory for ChromaDB storage
        collection_name: Name of the collection
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
    """
    # Only initialize with new parameters if they are provided
    if any([pdf_dir, db_dir, collection_name, chunk_size, chunk_overlap]):
        initialize_pdf_processor(
            pdf_dir=pdf_dir or "pdfs",
            db_dir=db_dir or "data/chromadb",
            collection_name=collection_name or "pdf_collection",
            chunk_size=chunk_size or 1000,
            chunk_overlap=chunk_overlap or 200
        )
    
    process_all_pdfs(pdf_dir=pdf_dir)

if __name__ == "__main__":
    process_pdfs()