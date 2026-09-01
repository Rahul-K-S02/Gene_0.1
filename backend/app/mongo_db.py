import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger("generisk.mongodb")

class MongoService:
    def __init__(self):
        self.is_connected = False
        self.client = None
        self.db = None
        self._init_connection()

    def _init_connection(self):
        if settings.MONGODB_URI:
            try:
                import pymongo
                self.client = pymongo.MongoClient(
                    settings.MONGODB_URI,
                    serverSelectionTimeoutMS=3000
                )
                # Verify connection
                self.client.admin.command('ping')
                self.db = self.client[settings.MONGODB_DB_NAME]
                self.is_connected = True
                logger.info(f"Connected to remote MongoDB Atlas database: {settings.MONGODB_DB_NAME}")
                return
            except Exception as e:
                logger.warning(f"MongoDB Atlas connection failed: {e}. Falling back to persistent document store.")
                self.is_connected = False
        
        # Local document store fallback using SQLite table in data/doc_store.db
        self._init_local_doc_store()

    def _init_local_doc_store(self):
        self.doc_db_path = settings.DATA_DIR / "generisk_docs.db"
        with sqlite3.connect(str(self.doc_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_collections (
                    collection_name TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    user_id TEXT,
                    created_at TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (collection_name, doc_id)
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_user ON document_collections(collection_name, user_id);")
            conn.commit()
        logger.info(f"Initialized local document store at {self.doc_db_path}")

    # --- User Management ---
    def create_user(self, user_doc: Dict[str, Any]) -> bool:
        if self.is_connected and self.db is not None:
            try:
                self.db.users.create_index("email", unique=True)
                self.db.users.insert_one(user_doc)
                return True
            except Exception as ex:
                logger.warning(f"MongoDB create_user failed: {ex}")
                return False

        # Fallback local doc store
        try:
            with sqlite3.connect(str(self.doc_db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO document_collections (collection_name, doc_id, user_id, created_at, payload) VALUES (?, ?, ?, ?, ?)",
                    ("users", user_doc["user_id"], user_doc["email"], user_doc["created_at"], json.dumps(user_doc))
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            logger.error(f"Doc store error in create_user: {e}")
            return False

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        clean_email = email.lower().strip()
        if self.is_connected and self.db is not None:
            try:
                res = self.db.users.find_one({"email": clean_email}, {"_id": 0})
                return dict(res) if res else None
            except Exception:
                pass

        # Fallback
        with sqlite3.connect(str(self.doc_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT payload FROM document_collections WHERE collection_name = 'users' AND user_id = ?",
                (clean_email,)
            )
            row = cursor.fetchone()
            return json.loads(row[0]) if row else None

    # --- Analysis History ---
    def save_analysis_history(self, history_doc: Dict[str, Any]) -> str:
        doc_id = history_doc.get("history_id", f"hist_{int(datetime.utcnow().timestamp())}")
        history_doc["history_id"] = doc_id
        user_id = history_doc.get("user_id", "guest")

        if self.is_connected and self.db is not None:
            try:
                self.db.analysis_history.insert_one(history_doc)
                return doc_id
            except Exception as ex:
                logger.warning(f"MongoDB save_history failed: {ex}")

        # Fallback
        with sqlite3.connect(str(self.doc_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO document_collections (collection_name, doc_id, user_id, created_at, payload) VALUES (?, ?, ?, ?, ?)",
                ("analysis_history", doc_id, user_id, history_doc.get("timestamp", datetime.utcnow().isoformat()), json.dumps(history_doc))
            )
            conn.commit()
        return doc_id

    def get_user_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            try:
                cursor = self.db.analysis_history.find(
                    {"user_id": user_id}, {"_id": 0}
                ).sort("timestamp", -1).limit(limit)
                return list(cursor)
            except Exception as ex:
                logger.warning(f"MongoDB get_history failed: {ex}")

        # Fallback
        with sqlite3.connect(str(self.doc_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT payload FROM document_collections WHERE collection_name = 'analysis_history' AND user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            )
            rows = cursor.fetchall()
            return [json.loads(r[0]) for r in rows]

    def delete_history_item(self, doc_id: str, user_id: str) -> bool:
        if self.is_connected and self.db is not None:
            try:
                self.db.analysis_history.delete_one({"history_id": doc_id, "user_id": user_id})
                return True
            except Exception:
                return False

        with sqlite3.connect(str(self.doc_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM document_collections WHERE collection_name = 'analysis_history' AND doc_id = ? AND user_id = ?",
                (doc_id, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0

mongo_service = MongoService()
