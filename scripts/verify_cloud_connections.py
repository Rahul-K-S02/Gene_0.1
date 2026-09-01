import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent / "backend"
load_dotenv(BASE_DIR / ".env")

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(title):
    print(f"\n{CYAN}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{RESET}")

def test_groq():
    print_header("1. Testing Groq API Connection (LLaMA 3.1)")
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        print(f"{YELLOW}[SKIPPED]{RESET} GROQ_API_KEY is not set in backend/.env.")
        print(f"   -> Backend will use deterministic clinical narrative synthesizer.")
        return False

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        t0 = time.time()
        res = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=[{"role": "user", "content": "Respond with the word 'CONNECTED' if you receive this."}],
            max_tokens=10
        )
        elapsed = time.time() - t0
        reply = res.choices[0].message.content.strip()
        print(f"{GREEN}[SUCCESS]{RESET} Groq Cloud API connected successfully!")
        print(f"   * Model: {os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')}")
        print(f"   * Latency: {elapsed:.2f}s")
        print(f"   * Live Response: '{reply}'")
        return True
    except Exception as e:
        print(f"{RED}[FAILED]{RESET} Groq connection error: {e}")
        return False

def test_qdrant():
    print_header("2. Testing Qdrant Vector Cloud Connection")
    qdrant_url = os.getenv("QDRANT_URL", "")
    qdrant_key = os.getenv("QDRANT_API_KEY", "")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "generisk_medical_rag")

    if not qdrant_url:
        print(f"{YELLOW}[SKIPPED]{RESET} QDRANT_URL is not set in backend/.env.")
        print(f"   -> Backend will use in-memory fast vector / lexical search.")
        return False

    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=qdrant_url, api_key=qdrant_key if qdrant_key else None)
        collections = client.get_collections().collections
        c_names = [c.name for c in collections]
        print(f"{GREEN}[SUCCESS]{RESET} Qdrant Vector Cloud connected successfully!")
        print(f"   * Cluster URL: {qdrant_url}")
        print(f"   * Collections Found: {c_names}")
        if collection_name in c_names:
            count = client.count(collection_name=collection_name).count
            print(f"   * Active Collection '{collection_name}': {count} vectors indexed.")
        else:
            print(f"   * Note: Collection '{collection_name}' not created yet. Run: python scripts/setup_qdrant_collection.py")
        return True
    except Exception as e:
        print(f"{RED}[FAILED]{RESET} Qdrant connection error: {e}")
        return False

def test_turso():
    print_header("3. Testing Turso Cloud Database Connection")
    db_url = os.getenv("TURSO_DATABASE_URL", "")
    auth_token = os.getenv("TURSO_AUTH_TOKEN", "")

    if not db_url or not auth_token:
        print(f"{YELLOW}[SKIPPED]{RESET} TURSO_DATABASE_URL / TURSO_AUTH_TOKEN not set in backend/.env.")
        print(f"   -> Backend will use local SQLite database at backend/data/generisk.db.")
        return False

    try:
        import libsql_experimental as libsql
        conn = libsql.connect(db_url, auth_token=auth_token)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM gwas_weights;")
        count = cursor.fetchone()[0]
        print(f"{GREEN}[SUCCESS]{RESET} Turso Cloud Database connected successfully!")
        print(f"   * Database: {db_url}")
        print(f"   * GWAS Weights Seeded: {count} variants")
        return True
    except Exception as e:
        print(f"{RED}[FAILED]{RESET} Turso connection error: {e}")
        return False

def test_mongodb():
    print_header("4. Testing MongoDB Atlas Cloud Connection")
    mongo_uri = os.getenv("MONGODB_URI", "")
    db_name = os.getenv("MONGODB_DB_NAME", "generisk_db")

    if not mongo_uri:
        print(f"{YELLOW}[SKIPPED]{RESET} MONGODB_URI is not set in backend/.env.")
        print(f"   -> Backend will use local document store at backend/data/generisk_docs.db.")
        return False

    try:
        import pymongo
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=4000)
        client.admin.command('ping')
        db = client[db_name]
        users_count = db.users.count_documents({})
        history_count = db.analysis_history.count_documents({})
        print(f"{GREEN}[SUCCESS]{RESET} MongoDB Atlas Cloud connected successfully!")
        print(f"   * Database: {db_name}")
        print(f"   * Users in DB: {users_count}")
        print(f"   * Historical Reports in DB: {history_count}")
        return True
    except Exception as e:
        print(f"{RED}[FAILED]{RESET} MongoDB Atlas connection error: {e}")
        return False

def test_google_oauth():
    print_header("5. Testing Google Cloud OAuth 2.0 Credentials")
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
    callback_url = os.getenv("GOOGLE_CALLBACK_URL", "http://localhost:8000/api/v1/auth/google/callback")

    if not client_id:
        print(f"{YELLOW}[SKIPPED]{RESET} GOOGLE_CLIENT_ID is not set in backend/.env.")
        print(f"   -> System will use verified instant demo authentication.")
        return False

    print(f"{GREEN}[CONFIGURED]{RESET} Google OAuth 2.0 Client ID detected!")
    print(f"   * Client ID: {client_id[:16]}...apps.googleusercontent.com")
    print(f"   * Client Secret: {'[SET]' if client_secret else '[NOT SET / GIS CLIENT-SIDE ONLY]'}")
    print(f"   * Redirect Callback URL: {callback_url}")
    return True

def main():
    print(f"{BOLD}{CYAN}============================================================")
    print("   GeneRisk Cloud Connection Verifier & Inspector")
    print(f"============================================================{RESET}")

    groq_ok = test_groq()
    qdrant_ok = test_qdrant()
    turso_ok = test_turso()
    mongo_ok = test_mongodb()
    google_ok = test_google_oauth()

    print(f"\n{BOLD}{CYAN}============================================================")
    print("   Connection Summary Status")
    print(f"============================================================{RESET}")
    print(f" * Groq LLaMA 3.1:      {GREEN if groq_ok else YELLOW}{'LIVE CLOUD API' if groq_ok else 'LOCAL FALLBACK'}{RESET}")
    print(f" * Qdrant Vector Cloud: {GREEN if qdrant_ok else YELLOW}{'LIVE CLOUD CLUSTER' if qdrant_ok else 'LOCAL IN-MEMORY'}{RESET}")
    print(f" * Turso Database:      {GREEN if turso_ok else YELLOW}{'LIVE CLOUD SQLITE' if turso_ok else 'LOCAL SQLITE'}{RESET}")
    print(f" * MongoDB Atlas:       {GREEN if mongo_ok else YELLOW}{'LIVE ATLAS CLUSTER' if mongo_ok else 'LOCAL DOC STORE'}{RESET}")
    print(f" * Google OAuth 2.0:    {GREEN if google_ok else YELLOW}{'CONFIGURED (GOOGLE CLOUD)' if google_ok else 'LOCAL DEMO AUTH'}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")

if __name__ == "__main__":
    main()
