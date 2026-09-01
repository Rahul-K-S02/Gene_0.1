import logging
from typing import Dict, List
from app.database import fetch_all
from app.schemas import PharmGKBAnnotation

logger = logging.getLogger("generisk.pharmgkb")

def lookup_pharmgkb_variants(user_dosages: Dict[str, float]) -> List[PharmGKBAnnotation]:
    """
    Checks user's variant dosages against PharmGKB actionable clinical pharmacogenomics records.
    """
    if not user_dosages:
        return []

    active_rsids = [rsid for rsid, dosage in user_dosages.items() if dosage >= 1.0]
    if not active_rsids:
        return []

    placeholders = ",".join(["?"] * len(active_rsids))
    query = f"""
    SELECT rsid, gene, drug, phenotype_category, clinical_recommendation, level_of_evidence
    FROM pharmgkb_variants
    WHERE rsid IN ({placeholders})
    """
    
    rows = fetch_all(query, tuple(active_rsids))
    results = []
    
    for r in rows:
        results.append(PharmGKBAnnotation(
            rsid=r["rsid"],
            gene=r["gene"],
            drug=r["drug"],
            phenotype_category=r["phenotype_category"],
            clinical_recommendation=r["clinical_recommendation"],
            level_of_evidence=r["level_of_evidence"]
        ))
        
    logger.info(f"Identified {len(results)} PharmGKB pharmacogenomic alerts.")
    return results
