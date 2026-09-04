import json
import logging
import sqlite3
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple

from app.config import settings

logger = logging.getLogger("generisk.database")

class DatabaseManager:
    def __init__(self):
        self.is_turso_active = False
        self.last_used_source = "sqlite"
        self._init_local_db()
        self._check_turso_connection()

    def _init_local_db(self):
        """Initializes local SQLite tables."""
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(settings.LOCAL_DB_PATH), check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS gwas_weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rsid TEXT NOT NULL,
                chromosome TEXT NOT NULL,
                position INTEGER NOT NULL,
                gene TEXT NOT NULL,
                disease_id TEXT NOT NULL,
                disease_name TEXT NOT NULL,
                effect_allele TEXT NOT NULL,
                other_allele TEXT NOT NULL,
                beta REAL NOT NULL,
                maf REAL NOT NULL,
                p_value REAL NOT NULL,
                source_pmid TEXT,
                UNIQUE(rsid, disease_id)
            );
            CREATE INDEX IF NOT EXISTS idx_gwas_rsid ON gwas_weights(rsid);
            CREATE INDEX IF NOT EXISTS idx_gwas_disease ON gwas_weights(disease_id);

            CREATE TABLE IF NOT EXISTS clinvar_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rsid TEXT NOT NULL,
                chromosome TEXT,
                position INTEGER,
                gene TEXT NOT NULL,
                clinical_significance TEXT NOT NULL,
                review_status TEXT,
                phenotype TEXT NOT NULL,
                accession TEXT,
                UNIQUE(rsid, phenotype)
            );
            CREATE INDEX IF NOT EXISTS idx_clinvar_rsid ON clinvar_variants(rsid);

            CREATE TABLE IF NOT EXISTS pharmgkb_variants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rsid TEXT NOT NULL,
                gene TEXT NOT NULL,
                drug TEXT NOT NULL,
                phenotype_category TEXT NOT NULL,
                clinical_recommendation TEXT NOT NULL,
                level_of_evidence TEXT NOT NULL,
                variant_allele TEXT,
                UNIQUE(rsid, drug)
            );
            CREATE INDEX IF NOT EXISTS idx_pharmgkb_rsid ON pharmgkb_variants(rsid);

            CREATE TABLE IF NOT EXISTS disease_reference_stats (
                disease_id TEXT PRIMARY KEY,
                disease_name TEXT NOT NULL,
                mean_raw_prs REAL NOT NULL,
                sd_raw_prs REAL NOT NULL,
                baseline_10yr_risk REAL NOT NULL,
                lifestyle_weight REAL NOT NULL DEFAULT 0.40,
                genetic_weight REAL NOT NULL DEFAULT 0.60
            );

            CREATE TABLE IF NOT EXISTS sync_state (
                service_name TEXT PRIMARY KEY,
                last_synced_at TEXT NOT NULL,
                record_count INTEGER NOT NULL,
                status TEXT NOT NULL,
                details TEXT
            );
            """)
            conn.commit()
        logger.info(f"Local SQLite database initialized at {settings.LOCAL_DB_PATH}")

    def _check_turso_connection(self):
        """Verifies remote Turso connection via LibSQL pipeline API."""
        if not settings.TURSO_DATABASE_URL or not settings.TURSO_AUTH_TOKEN:
            self.is_turso_active = False
            return

        try:
            base_url = settings.TURSO_DATABASE_URL.replace("libsql://", "https://")
            url = f"{base_url}/v2/pipeline"
            payload = json.dumps({
                "requests": [{"type": "execute", "stmt": {"sql": "SELECT 1;"}}]
            }).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {settings.TURSO_AUTH_TOKEN}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status == 200:
                    self.is_turso_active = True
                    logger.info("Connected to remote Turso database.")
                    self._ensure_turso_sync_table()
                    return
        except Exception as ex:
            logger.warning(f"Turso connection check failed: {ex}. Using local SQLite.")
            self.is_turso_active = False

    def _ensure_turso_sync_table(self):
        """Ensures sync_state table exists in remote Turso."""
        try:
            self.execute_turso_query("""
                CREATE TABLE IF NOT EXISTS sync_state (
                    service_name TEXT PRIMARY KEY,
                    last_synced_at TEXT NOT NULL,
                    record_count INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT
                );
            """)
        except Exception:
            pass

    def execute_turso_query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a parameterized SQL query on remote Turso via LibSQL HTTP Pipeline API."""
        base_url = settings.TURSO_DATABASE_URL.replace("libsql://", "https://")
        url = f"{base_url}/v2/pipeline"

        # Format parameters for LibSQL protocol
        args = []
        for p in params:
            if isinstance(p, int):
                args.append({"type": "integer", "value": str(p)})
            elif isinstance(p, float):
                args.append({"type": "float", "value": p})
            elif p is None:
                args.append({"type": "null"})
            else:
                args.append({"type": "text", "value": str(p)})

        payload = json.dumps({
            "requests": [{"type": "execute", "stmt": {"sql": sql, "args": args}}]
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {settings.TURSO_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
        )

        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            if not results:
                return []
            
            res_obj = results[0]
            if res_obj.get("type") == "error":
                raise RuntimeError(res_obj.get("error", {}).get("message", "Turso error"))

            exec_res = res_obj.get("response", {}).get("result", {})
            cols = [c["name"] for c in exec_res.get("cols", [])]
            rows = exec_res.get("rows", [])

            mapped_rows = []
            for r in rows:
                row_dict = {}
                for idx, col_name in enumerate(cols):
                    cell = r[idx] if idx < len(r) else {}
                    val = cell.get("value") if isinstance(cell, dict) else cell
                    row_dict[col_name] = val
                mapped_rows.append(row_dict)

            return mapped_rows

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Executes query against remote Turso first (with automatic column mapping),
        falling back to local SQLite if Turso is unreachable.
        """
        if self.is_turso_active and settings.TURSO_DATABASE_URL:
            try:
                # Apply column mapping if querying GWAS or ClinVar
                adapted_query, adapted_params = self._adapt_query_for_turso(query, params)
                turso_rows = self.execute_turso_query(adapted_query, adapted_params)
                self.last_used_source = "turso"
                return self._adapt_rows_from_turso(turso_rows, query)
            except Exception as ex:
                logger.warning(f"Remote Turso query failed: {ex}. Falling back to SQLite.")
                self.is_turso_active = False

        # SQLite Fallback
        self.last_used_source = "sqlite_fallback"
        with sqlite3.connect(str(settings.LOCAL_DB_PATH), check_same_thread=False) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    def _adapt_write_for_turso(self, query: str, params: tuple) -> tuple:
        """
        Rewrites local-schema INSERT statements to match the remote Turso schema.
        Since the Turso schema now matches the local schema exactly, this just returns the unmodified query.
        """
        return query, params

    def execute_query(self, query: str, params: tuple = ()) -> int:
        """Executes INSERT/UPDATE statement across active database."""
        if self.is_turso_active and settings.TURSO_DATABASE_URL:
            try:
                adapted_query, adapted_params = self._adapt_write_for_turso(query, params)
                self.execute_turso_query(adapted_query, adapted_params)
                self.last_used_source = "turso"
            except Exception as ex:
                logger.warning(f"Turso write failed: {ex}. Writing to local SQLite.")
                # Don't permanently disable turso for write errors - only for connectivity errors
                # Keep turso active so reads still work

        with sqlite3.connect(str(settings.LOCAL_DB_PATH), check_same_thread=False) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def get_sync_state(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves last synchronization state for a service."""
        return self.fetch_one(
            "SELECT service_name, last_synced_at, record_count, status, details FROM sync_state WHERE service_name = ?",
            (service_name,)
        )

    def set_sync_state(self, service_name: str, last_synced_at: str, record_count: int, status: str, details: str = ""):
        """Updates synchronization state."""
        sql = """
        INSERT OR REPLACE INTO sync_state (service_name, last_synced_at, record_count, status, details)
        VALUES (?, ?, ?, ?, ?)
        """
        self.execute_query(sql, (service_name, last_synced_at, record_count, status, details))

    # --- Column Mapping Adapter for Turso ---
    def _adapt_query_for_turso(self, query: str, params: tuple) -> Tuple[str, tuple]:
        """Pass-through since Turso schema matches local schema."""
        return query, params

    def _adapt_rows_from_turso(self, rows: List[Dict[str, Any]], original_query: str) -> List[Dict[str, Any]]:
        """Normalizes rows returned from remote Turso."""
        return [dict(r) for r in rows]

db_manager = DatabaseManager()

# Public helper functions for backward compatibility
def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    return db_manager.fetch_all(query, params)

def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    return db_manager.fetch_one(query, params)

def execute_query(query: str, params: tuple = ()) -> int:
    return db_manager.execute_query(query, params)

def execute_script(script: str):
    with sqlite3.connect(str(settings.LOCAL_DB_PATH), check_same_thread=False) as conn:
        conn.executescript(script)
        conn.commit()

def init_tables():
    db_manager._init_local_db()
