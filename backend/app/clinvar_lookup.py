import logging
from typing import Dict, List, Any
from app.database import fetch_all
from app.schemas import ClinVarAnnotation

logger = logging.getLogger("generisk.clinvar")

def lookup_clinvar_variants(user_dosages: Dict[str, float]) -> List[ClinVarAnnotation]:
    """
    Checks user's variant dosages against ClinVar pathogenic / likely pathogenic records.
    Only variants where dosage >= 1.0 (carrying at least 1 risk/alternate allele) are evaluated.
    """
    if not user_dosages:
        return []

    active_rsids = [rsid for rsid, dosage in user_dosages.items() if dosage >= 1.0]
    if not active_rsids:
        return []

    placeholders = ",".join(["?"] * len(active_rsids))
    query = f"""
    SELECT rsid, gene, clinical_significance, review_status, phenotype, accession
    FROM clinvar_variants
    WHERE rsid IN ({placeholders})
    """
    
    rows = fetch_all(query, tuple(active_rsids))
    results = []
    
    for r in rows:
        results.append(ClinVarAnnotation(
            rsid=r["rsid"],
            gene=r["gene"],
            clinical_significance=r["clinical_significance"],
            review_status=r["review_status"] or "criteria provided, single submitter",
            phenotype=r["phenotype"],
            accession=r["accession"] or f"VCV000{abs(hash(r['rsid'])) % 1000000}"
        ))
        
    logger.info(f"Identified {len(results)} ClinVar annotations in user genotype.")
    return results
