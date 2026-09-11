import os
import chromadb
from chromadb.config import Settings
from django.conf import settings

# Initialize ChromaDB client using a local persistent directory
CHROMA_PERSIST_DIR = os.path.join(settings.BASE_DIR, "chroma_db")
chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

from celery import shared_task

def get_or_create_collection(project_id):
    """Retrieve or create a ChromaDB collection for a specific project."""
    collection_name = f"project_{project_id}"
    return chroma_client.get_or_create_collection(name=collection_name)

@shared_task
def index_project_files(project_id, extracted_path):
    """
    Chunks and indexes all Python files in the extracted project path
    into ChromaDB for RAG context during AI generation.
    """
    collection = get_or_create_collection(project_id)
    
    documents = []
    metadatas = []
    ids = []
    
    for root, dirs, files in os.walk(extracted_path):
        dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "venv", "env"]]
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, extracted_path).replace("\\", "/")
                
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        
                    # Simple chunking by file for now. 
                    # For a production system, we'd chunk by class/function or token count.
                    documents.append(content)
                    metadatas.append({"file_path": rel_path})
                    ids.append(rel_path)
                    
                except Exception as e:
                    print(f"Failed to read {rel_path} for indexing: {e}")

    if documents:
        # Upsert documents into the collection
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    return True

def retrieve_relevant_context(project_id, query, n_results=3):
    """
    Queries the vector database to find files similar to the query.
    """
    try:
        collection = get_or_create_collection(project_id)
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        context_files = []
        if results and results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i]
                context_files.append({
                    "file_path": meta["file_path"],
                    "content": doc
                })
        return context_files
    except Exception as e:
        print(f"ChromaDB retrieval error: {e}")
        return []
