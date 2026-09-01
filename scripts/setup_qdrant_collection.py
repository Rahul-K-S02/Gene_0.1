import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

from app.config import settings
from app.rag_pipeline import DEFAULT_KNOWLEDGE_CHUNKS

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def setup_qdrant_cloud():
    print(f"\n{CYAN}{'='*65}")
    print(f"  {BOLD}Qdrant Vector Cloud Collection Setup & Vector Indexer{RESET}")
    print(f"{CYAN}{'='*65}{RESET}\n")

    qdrant_url = settings.QDRANT_URL
    qdrant_key = settings.QDRANT_API_KEY
    collection_name = settings.QDRANT_COLLECTION_NAME

    if not qdrant_url:
        print(f"{YELLOW}[NOTICE]{RESET} QDRANT_URL is not configured in backend/.env.")
        print(f"   * The app will run using high-speed in-memory vector & lexical search.")
        return

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import Distance, VectorParams, PointStruct
        from fastembed import TextEmbedding

        print(f"{CYAN}[1/3]{RESET} Connecting to Qdrant Cloud at {qdrant_url}...")
        client = QdrantClient(url=qdrant_url, api_key=qdrant_key if qdrant_key else None)
        
        # Check existing collections
        existing = [c.name for c in client.get_collections().collections]
        if collection_name in existing:
            count = client.count(collection_name=collection_name).count
            print(f"   * Collection '{collection_name}' already exists with {count} points.")
        else:
            print(f"   * Creating collection '{collection_name}' (384-dimensional cosine distance)...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            print(f"{GREEN}[SUCCESS]{RESET} Collection '{collection_name}' created!")

        print(f"\n{CYAN}[2/3]{RESET} Generating embeddings using FastEmbed (BAAI/bge-small-en-v1.5)...")
        embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        texts = [f"{c['topic']}: {c['text']}" for c in DEFAULT_KNOWLEDGE_CHUNKS]
        embeddings = list(embedder.embed(texts))
        
        print(f"\n{CYAN}[3/3]{RESET} Uploading {len(DEFAULT_KNOWLEDGE_CHUNKS)} clinical evidence vectors to '{collection_name}'...")
        points = []
        for i, (chunk, emb) in enumerate(zip(DEFAULT_KNOWLEDGE_CHUNKS, embeddings)):
            points.append(PointStruct(
                id=100 + i + 1,  # Offset ID to preserve existing user points
                vector=emb.tolist(),
                payload=chunk
            ))
        
        client.upsert(collection_name=collection_name, points=points)
        count = client.count(collection_name=collection_name).count
        print(f"{GREEN}[COMPLETE]{RESET} Successfully indexed {count} medical knowledge vectors in Qdrant Cloud '{collection_name}'!")

    except Exception as e:
        print(f"{RED}[ERROR]{RESET} Failed to setup Qdrant Cloud collection: {e}")

if __name__ == "__main__":
    setup_qdrant_cloud()
