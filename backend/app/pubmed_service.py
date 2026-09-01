import os
import time
import uuid
import logging
import threading
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.config import settings
from app.database import db_manager

logger = logging.getLogger("generisk.pubmed")

DISEASE_SEARCH_QUERIES = {
    "Type 2 Diabetes": "Type 2 Diabetes[Title/Abstract] AND (genetics[Title/Abstract] OR lifestyle[Title/Abstract] OR prevention[Title/Abstract])",
    "Coronary Artery Disease": "Coronary Artery Disease[Title/Abstract] AND (polygenic[Title/Abstract] OR genetics[Title/Abstract] OR lifestyle[Title/Abstract])",
    "Breast Cancer": "Breast Cancer[Title/Abstract] AND (BRCA1[Title/Abstract] OR screening[Title/Abstract] OR prevention[Title/Abstract])",
    "Alzheimer's Disease": "Alzheimer Disease[Title/Abstract] AND (APOE[Title/Abstract] OR polygenic[Title/Abstract] OR prevention[Title/Abstract])",
    "Hypertension": "Hypertension[Title/Abstract] AND (genetics[Title/Abstract] OR DASH diet[Title/Abstract] OR sodium[Title/Abstract])"
}

class PubMedService:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self._is_syncing = False

    def search_pmids(self, query: str, max_results: int = 15) -> List[str]:
        """Queries NCBI ESearch for PMIDs matching clinical disease criteria."""
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": str(max_results),
            "sort": "pub_date",
            "retmode": "json"
        }
        if settings.NCBI_EMAIL:
            params["email"] = settings.NCBI_EMAIL
        if settings.NCBI_API_KEY:
            params["api_key"] = settings.NCBI_API_KEY

        url = f"{self.base_url}/esearch.fcgi?{urllib.parse.urlencode(params)}"
        
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "GeneRisk-Genomics-Platform/2.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    import json
                    data = json.loads(resp.read().decode("utf-8"))
                    id_list = data.get("esearchresult", {}).get("idlist", [])
                    return id_list
            except Exception as e:
                wait_time = (2 ** attempt) * 1.5
                logger.warning(f"NCBI ESearch attempt {attempt+1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

        return []

    def fetch_article_summaries(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """Fetches XML records for a batch of PMIDs via NCBI EFetch."""
        if not pmids:
            return []

        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }
        if settings.NCBI_EMAIL:
            params["email"] = settings.NCBI_EMAIL
        if settings.NCBI_API_KEY:
            params["api_key"] = settings.NCBI_API_KEY

        url = f"{self.base_url}/efetch.fcgi?{urllib.parse.urlencode(params)}"
        articles = []

        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "GeneRisk-Genomics-Platform/2.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    xml_content = resp.read()
                    root = ET.fromstring(xml_content)

                    for article_el in root.findall(".//PubmedArticle"):
                        pmid_el = article_el.find(".//MedlineCitation/PMID")
                        pmid = pmid_el.text.strip() if pmid_el is not None and pmid_el.text else ""

                        title_el = article_el.find(".//ArticleTitle")
                        title = "".join(title_el.itertext()).strip() if title_el is not None else ""

                        abstract_texts = []
                        for ab in article_el.findall(".//AbstractText"):
                            label = ab.get("Label", "")
                            text = "".join(ab.itertext()).strip()
                            if text:
                                if label:
                                    abstract_texts.append(f"{label}: {text}")
                                else:
                                    abstract_texts.append(text)
                        
                        abstract = " ".join(abstract_texts).strip()

                        # Skip records without abstract
                        if not abstract or len(abstract) < 40 or not title:
                            continue

                        journal_el = article_el.find(".//Journal/Title")
                        journal = journal_el.text.strip() if journal_el is not None and journal_el.text else "PubMed Indexed Journal"

                        year_el = article_el.find(".//JournalIssue/PubDate/Year") or article_el.find(".//DateCompleted/Year")
                        try:
                            year = int(year_el.text.strip()) if year_el is not None and year_el.text else 2024
                        except ValueError:
                            year = 2024

                        articles.append({
                            "pmid": pmid,
                            "title": title,
                            "abstract": abstract,
                            "journal": journal,
                            "publication_year": year,
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                        })
                    
                    return articles
            except Exception as e:
                wait_time = (2 ** attempt) * 2.0
                logger.warning(f"NCBI EFetch attempt {attempt+1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

        return articles

    def chunk_text(self, text: str, max_chars: int = 1200) -> List[str]:
        """Splits long abstracts into chunks preserving sentence boundaries."""
        if len(text) <= max_chars:
            return [text]

        sentences = text.replace(". ", ".\n").split("\n")
        chunks = []
        current_chunk = []
        current_len = 0

        for s in sentences:
            s_len = len(s)
            if current_len + s_len > max_chars and current_chunk:
                chunks.append(" ".join(current_chunk).strip())
                current_chunk = [s]
                current_len = s_len
            else:
                current_chunk.append(s)
                current_len += s_len

        if current_chunk:
            chunks.append(" ".join(current_chunk).strip())

        return chunks

    def sync_pubmed_to_qdrant(self, max_per_disease: int = 15) -> int:
        """Fetches, chunks, embeds, and indexes PubMed articles into Qdrant collection major_project."""
        if not settings.QDRANT_URL:
            logger.warning("QDRANT_URL not configured. Skipping PubMed synchronization.")
            return 0

        from qdrant_client import QdrantClient
        from qdrant_client.http.models import Distance, VectorParams, PointStruct
        from fastembed import TextEmbedding

        q_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)
        embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        collection_name = settings.QDRANT_COLLECTION_NAME

        # Verify collection
        existing_cols = [c.name for c in q_client.get_collections().collections]
        if collection_name not in existing_cols:
            q_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

        total_upserted = 0
        now_iso = datetime.utcnow().isoformat() + "Z"

        for disease_name, query in DISEASE_SEARCH_QUERIES.items():
            logger.info(f"Searching PubMed for '{disease_name}'...")
            pmids = self.search_pmids(query, max_results=max_per_disease)
            if not pmids:
                continue

            time.sleep(0.4)  # Respect NCBI rate limit (max 3 req/sec without API key)
            articles = self.fetch_article_summaries(pmids)
            logger.info(f"Fetched {len(articles)} PubMed articles for '{disease_name}'.")

            points = []
            for art in articles:
                chunks = self.chunk_text(art["abstract"])
                for chunk_idx, chunk_text in enumerate(chunks):
                    # Full readable document representation
                    doc_text = f"{art['title']}\n\nAbstract: {chunk_text}\nJournal: {art['journal']} ({art['publication_year']})"
                    
                    # Embed using FastEmbed
                    emb = list(embedder.embed([doc_text]))[0].tolist()

                    # Deterministic UUID preventing duplicates
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"PubMed_{art['pmid']}_{chunk_idx}"))

                    payload = {
                        "document": doc_text,
                        "title": art["title"],
                        "source": "PubMed",
                        "pmid": art["pmid"],
                        "url": art["url"],
                        "disease": disease_name,
                        "journal": art["journal"],
                        "publication_year": art["publication_year"],
                        "chunk_number": chunk_idx,
                        "fetched_at": now_iso
                    }

                    points.append(PointStruct(
                        id=point_id,
                        # Use the named vector as defined in the Qdrant collection schema
                        vector={"fast-bge-small-en-v1.5": emb},
                        payload=payload
                    ))

            if points:
                q_client.upsert(collection_name=collection_name, points=points)
                total_upserted += len(points)
                logger.info(f"Upserted {len(points)} vector points for '{disease_name}' into '{collection_name}'.")

            time.sleep(0.5)

        # Update sync_state in database
        db_manager.set_sync_state(
            service_name="pubmed_knowledge",
            last_synced_at=now_iso,
            record_count=total_upserted,
            status="completed",
            details=f"Indexed {total_upserted} PubMed chunks into {collection_name}"
        )
        logger.info(f"PubMed synchronization complete. Total points upserted: {total_upserted}.")
        return total_upserted

    def ensure_pubmed_knowledge_ready(self):
        """
        Background startup check:
        1. Checks last sync timestamp in sync_state table.
        2. If missing or older than PUBMED_SYNC_MAX_AGE_DAYS (7 days), launches non-blocking sync.
        3. Never blocks user requests and never deletes existing points.
        """
        if not settings.PUBMED_SYNC_ENABLED:
            return

        if self._is_syncing:
            return

        state = db_manager.get_sync_state("pubmed_knowledge")
        should_sync = False

        if not state:
            should_sync = True
        else:
            try:
                last_dt = datetime.fromisoformat(state["last_synced_at"].replace("Z", "+00:00"))
                if datetime.utcnow().replace(tzinfo=last_dt.tzinfo) - last_dt > timedelta(days=settings.PUBMED_SYNC_MAX_AGE_DAYS):
                    should_sync = True
            except Exception:
                should_sync = True

        if should_sync:
            self._is_syncing = True
            logger.info("Starting background PubMed synchronization into Qdrant collection 'major_project'...")
            t = threading.Thread(target=self._run_bg_sync, daemon=True)
            t.start()
        else:
            logger.info(f"PubMed knowledge is fresh (last synced: {state.get('last_synced_at')}).")

    def _run_bg_sync(self):
        try:
            self.sync_pubmed_to_qdrant(max_per_disease=settings.PUBMED_MAX_ARTICLES_PER_DISEASE)
        except Exception as e:
            logger.error(f"Background PubMed sync encountered error: {e}")
        finally:
            self._is_syncing = False

pubmed_service = PubMedService()

def ensure_pubmed_knowledge_ready():
    pubmed_service.ensure_pubmed_knowledge_ready()
