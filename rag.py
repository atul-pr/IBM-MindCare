"""
RAG (Retrieval-Augmented Generation) Module - WORKING IMPLEMENTATION
Handles document ingestion, vector storage, and context retrieval
for grounding AI responses in curated mental health resources.

WHY RAG:
- Grounds AI responses in verified mental health information
- Reduces hallucinations and incorrect advice
- Provides evidence-based coping strategies
- Ensures culturally appropriate content for Indian context
- Makes responses more reliable and trustworthy

HOW IT WORKS:
1. Documents are split into chunks (paragraphs)
2. Each chunk is converted to embeddings (vector representations)
3. Embeddings are stored in FAISS vector database
4. User query is converted to embedding
5. Similar chunks are retrieved from FAISS
6. Retrieved context is added to AI prompt
7. AI generates response grounded in retrieved information
"""

# Force CPU-only mode before importing ML libraries
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'       # Disable CUDA/GPU
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'        # Suppress all TF/transformers warnings
# HF_HOME covers all HuggingFace caches (replaces deprecated TRANSFORMERS_CACHE)
os.environ.setdefault('HF_HOME', '/tmp/hf_cache')
os.environ.setdefault('SENTENCE_TRANSFORMERS_HOME', '/tmp/hf_cache')

import pickle
from typing import List, Dict, Optional

# sentence_transformers, faiss, numpy are imported LAZILY inside functions.
# This prevents loading ~400MB of ML libraries at startup, which would OOM
# Railway's 512MB container before gunicorn can even bind to the port.

# Resolve paths relative to THIS file so they work regardless of CWD
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# CONFIGURATION
# ============================================================================

RAG_ENABLED = True  # Set to True to enable RAG
VECTOR_DB_PATH = os.path.join(_BASE_DIR, "data", "vector_store", "faiss_index.pkl")
DOCUMENTS_PATH = os.path.join(_BASE_DIR, "data", "documents")
CHUNK_SIZE = 500  # Characters per chunk
TOP_K_RESULTS = 2  # Number of relevant chunks to retrieve

# Embedding model (lightweight, works offline after first download)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions, fast, good quality

# Global variables
_embedding_model = None
_faiss_index = None
_chunks_metadata = []


# ============================================================================
# EMBEDDING MODEL
# ============================================================================

def get_embedding_model():
    """
    Load sentence transformer model for embeddings.
    Imported lazily — only called on first chat query, not at startup.
    """
    global _embedding_model

    if _embedding_model is None:
        # Lazy import — keeps startup memory under 100MB
        from sentence_transformers import SentenceTransformer
        print("Loading embedding model (first query — may take ~30s if downloading)...")
        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL,
            cache_folder=os.environ.get('HF_HOME', '/tmp/hf_cache')
        )
        print("Embedding model loaded!")

    return _embedding_model


# ============================================================================
# DOCUMENT INGESTION
# ============================================================================

def load_documents() -> List[str]:
    """
    Load all text documents from documents folder
    
    Returns:
        List[str]: List of document contents
    """
    documents = []
    
    if not os.path.exists(DOCUMENTS_PATH):
        print(f"Documents path not found: {DOCUMENTS_PATH}")
        return documents
    
    for filename in os.listdir(DOCUMENTS_PATH):
        if filename.endswith('.txt'):
            filepath = os.path.join(DOCUMENTS_PATH, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append(content)
                    print(f"Loaded: {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return documents


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """
    Split text into chunks by paragraphs
    
    WHY PARAGRAPHS:
    - Maintains semantic coherence
    - Better than arbitrary character splits
    - Each chunk is a complete thought
    
    Args:
        text (str): Document text
        chunk_size (int): Approximate characters per chunk
        
    Returns:
        List[str]: List of text chunks
    """
    # Split by double newlines (paragraphs)
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # If adding this paragraph exceeds chunk size, save current chunk
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk += "\n\n" + para if current_chunk else para
    
    # Add last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def ingest_documents() -> bool:
    """
    Ingest all documents into FAISS vector database
    
    PROCESS:
    1. Load documents from folder
    2. Split into chunks
    3. Generate embeddings for each chunk
    4. Build FAISS index
    5. Save to disk
    
    Returns:
        bool: Success status
    """
    global _faiss_index, _chunks_metadata
    
    try:
        print("\n" + "=" * 60)
        print("INGESTING DOCUMENTS INTO RAG SYSTEM")
        print("=" * 60)
        
        # Load documents
        documents = load_documents()
        if not documents:
            print("No documents found!")
            return False
        
        print(f"\nLoaded {len(documents)} document(s)")
        
        # Split into chunks
        all_chunks = []
        for doc_idx, doc in enumerate(documents):
            chunks = split_into_chunks(doc)
            for chunk in chunks:
                all_chunks.append(chunk)
                _chunks_metadata.append({
                    'text': chunk,
                    'doc_id': doc_idx,
                    'length': len(chunk)
                })
        
        print(f"Created {len(all_chunks)} chunks")
        
        # Generate embeddings
        print("\nGenerating embeddings...")
        import numpy as np
        model = get_embedding_model()
        embeddings = model.encode(all_chunks, show_progress_bar=True)
        
        # Build FAISS index
        print("\nBuilding FAISS index...")
        import faiss
        dimension = embeddings.shape[1]  # 384 for all-MiniLM-L6-v2
        _faiss_index = faiss.IndexFlatL2(dimension)  # L2 distance
        _faiss_index.add(embeddings.astype('float32'))
        
        print(f"FAISS index built with {_faiss_index.ntotal} vectors")
        
        # Save to disk
        os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)
        with open(VECTOR_DB_PATH, 'wb') as f:
            pickle.dump({
                'index': faiss.serialize_index(_faiss_index),
                'metadata': _chunks_metadata
            }, f)
        
        print(f"\n✅ RAG system ready!")
        print(f"Saved to: {VECTOR_DB_PATH}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error ingesting documents: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_vector_store() -> bool:
    """
    Load FAISS index from disk
    
    Returns:
        bool: Success status
    """
    global _faiss_index, _chunks_metadata
    
    if not os.path.exists(VECTOR_DB_PATH):
        print("Vector store not found. Run ingest_documents() first.")
        return False
    
    try:
        with open(VECTOR_DB_PATH, 'rb') as f:
            import faiss
            data = pickle.load(f)
            _faiss_index = faiss.deserialize_index(data['index'])
            _chunks_metadata = data['metadata']
        
        print(f"Loaded vector store: {_faiss_index.ntotal} vectors")
        return True
        
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return False


# ============================================================================
# CONTEXT RETRIEVAL
# ============================================================================

def retrieve_relevant_context(query: str, top_k: int = TOP_K_RESULTS) -> List[Dict]:
    """
    Retrieve relevant document chunks for a user query
    
    HOW IT WORKS:
    1. Convert query to embedding
    2. Search FAISS for similar chunks
    3. Return top-k most similar chunks
    
    Args:
        query (str): User's message
        top_k (int): Number of relevant chunks to return
        
    Returns:
        List[Dict]: List of relevant chunks with metadata
    """
    global _faiss_index, _chunks_metadata
    
    if not RAG_ENABLED:
        return []
    
    # Load vector store if not loaded
    if _faiss_index is None:
        if not load_vector_store():
            return []
    
    try:
        # Generate query embedding
        import numpy as np
        model = get_embedding_model()
        query_embedding = model.encode([query])
        
        # Search FAISS
        distances, indices = _faiss_index.search(
            query_embedding.astype('float32'), 
            top_k
        )
        
        # Retrieve chunks
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(_chunks_metadata):
                chunk = _chunks_metadata[idx]
                results.append({
                    'text': chunk['text'],
                    'score': float(distance),
                    'doc_id': chunk['doc_id']
                })
        
        return results
        
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return []


def format_context(chunks: List[Dict]) -> str:
    """
    Format retrieved chunks into readable context
    
    Args:
        chunks (List[Dict]): Retrieved document chunks
        
    Returns:
        str: Formatted context string
    """
    if not chunks:
        return ""
    
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        # Limit chunk length for prompt
        text = chunk['text'][:300] + "..." if len(chunk['text']) > 300 else chunk['text']
        context_parts.append(f"[{i}] {text}")
    
    return "\n\n".join(context_parts)


# ============================================================================
# MAIN RAG FUNCTION
# ============================================================================

def get_rag_context(user_message: str) -> str:
    """
    Get RAG context for user message
    
    This is the main function called by ai.py
    
    Args:
        user_message (str): User's message
        
    Returns:
        str: Formatted context to add to prompt
    """
    if not RAG_ENABLED:
        return ""
    
    chunks = retrieve_relevant_context(user_message)
    return format_context(chunks)


# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_rag():
    """
    Initialize RAG system on startup.
    Failures are caught and RAG is disabled gracefully — the app still works
    with pattern-based fallback responses.
    """
    global RAG_ENABLED

    if not RAG_ENABLED:
        print("RAG is disabled")
        return

    print("\nInitializing RAG system...")

    try:
        # Check if vector store exists
        if os.path.exists(VECTOR_DB_PATH):
            if load_vector_store():
                print("✅ RAG system loaded from disk")
                return
            else:
                print("Vector store corrupted. Rebuilding...")

        # Try to ingest documents
        print("Vector store not found. Ingesting documents...")
        if ingest_documents():
            print("✅ RAG system initialized")
        else:
            print("⚠️  RAG initialization failed — disabling RAG, app will use fallback responses.")
            RAG_ENABLED = False

    except Exception as e:
        print(f"⚠️  RAG system error: {e} — disabling RAG, app will use fallback responses.")
        RAG_ENABLED = False


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("RAG SYSTEM TEST")
    print("=" * 60)
    
    # Ingest documents
    if ingest_documents():
        # Test retrieval
        test_queries = [
            "I'm feeling anxious",
            "How do I manage stress?",
            "breathing exercises"
        ]
        
        for query in test_queries:
            print(f"\n\nQuery: '{query}'")
            print("-" * 60)
            context = get_rag_context(query)
            print(f"Retrieved context:\n{context}")
