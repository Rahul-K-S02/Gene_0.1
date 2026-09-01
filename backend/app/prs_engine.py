import math
import logging
from typing import Dict, List, Any, Optional
from scipy.stats import norm
from app.database import fetch_all, fetch_one

logger = logging.getLogger("generisk.prs_engine")

class PRSEngine:
    def __init__(self):
        pass

    def get_supported_panel(self) -> List[Dict[str, Any]]:
        """Returns the full GWAS SNP panel from database."""
        query = """
        SELECT rsid, gene, disease_id, disease_name, chromosome, position,
               effect_allele, other_allele, beta, maf, p_value, source_pmid
        FROM gwas_weights
        ORDER BY disease_id, chromosome, position
        """
        return fetch_all(query)

    def get_supported_rsids(self) -> set[str]:
        """Returns the set of rsIDs in the panel."""
        query = "SELECT DISTINCT rsid FROM gwas_weights"
        rows = fetch_all(query)
        return {r["rsid"] for r in rows}

    def compute_disease_prs(
        self,
        disease_id: str,
        user_dosages: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Computes standardized PRS and analytic normal CDF percentile for a specific disease.
        
        Formula:
        For each SNP i:
            z_i = (dosage_i - 2 * maf_i) / sqrt(2 * maf_i * (1 - maf_i))
            snp_contribution = beta_i * z_i
            
        Theoretical Reference Distribution (assuming independent clumped SNPs):
            mu_ref = sum(beta_i * 2 * maf_i)
            var_ref = sum(beta_i^2 * 2 * maf_i * (1 - maf_i))
            sigma_ref = sqrt(var_ref)
            
        Percentile:
            Phi(Z) * 100 via scipy.stats.norm.cdf or analytic erf
        """
        query = """
        SELECT rsid, gene, chromosome, position, effect_allele, other_allele, beta, maf, p_value
        FROM gwas_weights
        WHERE disease_id = ?
        """
        snps = fetch_all(query, (disease_id,))
        if not snps:
            logger.warning(f"No GWAS weights found for disease: {disease_id}")
            return {
                "disease_id": disease_id,
                "raw_score": 0.0,
                "standardized_z": 0.0,
                "percentile": 50.0,
                "snps_found": 0,
                "snps_total": 0,
                "confidence_score": 0.0,
                "snp_breakdown": []
            }

        total_snps = len(snps)
        found_snps = 0
        raw_score = 0.0
        standardized_z = 0.0
        
        # Analytic population mean and variance for standardization
        mu_pop = 0.0
        var_pop = 0.0
        
        snp_details = []

        for snp in snps:
            rsid = snp["rsid"]
            beta = float(snp["beta"])
            maf = float(snp["maf"])
            
            # Safeguard MAF to avoid division by zero
            maf = min(max(maf, 0.001), 0.999)
            
            # Population variance term: 2 * maf * (1 - maf)
            snp_var = 2.0 * maf * (1.0 - maf)
            snp_sd = math.sqrt(snp_var)
            
            mu_pop += beta * (2.0 * maf)
            var_pop += (beta ** 2) * snp_var

            if rsid in user_dosages:
                dosage = user_dosages[rsid]
                found_snps += 1
                raw_score += beta * dosage
                
                # Standardized SNP z-score
                z_i = (dosage - (2.0 * maf)) / snp_sd
                standardized_z += beta * z_i
                
                snp_details.append({
                    "rsid": rsid,
                    "gene": snp["gene"],
                    "dosage": dosage,
                    "beta": beta,
                    "maf": maf,
                    "contribution": beta * z_i,
                    "imputed": False
                })
            else:
                # Missing SNP: Impute to population mean (dosage = 2*maf => z_i = 0)
                # This maintains neutrality and prevents arbitrary bias
                imputed_dosage = 2.0 * maf
                raw_score += beta * imputed_dosage
                snp_details.append({
                    "rsid": rsid,
                    "gene": snp["gene"],
                    "dosage": imputed_dosage,
                    "beta": beta,
                    "maf": maf,
                    "contribution": 0.0,
                    "imputed": True
                })

        sigma_pop = math.sqrt(var_pop) if var_pop > 0 else 1.0
        
        # Final standardized Z-score relative to reference distribution
        normalized_z = (raw_score - mu_pop) / sigma_pop
        
        # Calculate percentile using standard normal CDF
        percentile = float(norm.cdf(normalized_z) * 100.0)
        percentile = min(max(percentile, 0.1), 99.9)

        confidence_score = float(found_snps / total_snps) if total_snps > 0 else 0.0

        return {
            "disease_id": disease_id,
            "raw_score": round(raw_score, 4),
            "standardized_z": round(normalized_z, 3),
            "percentile": round(percentile, 1),
            "snps_found": found_snps,
            "snps_total": total_snps,
            "confidence_score": round(confidence_score, 2),
            "snp_breakdown": snp_details
        }

    def compute_all_prs(self, user_dosages: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Computes PRS for all diseases available in the database."""
        query = "SELECT DISTINCT disease_id, disease_name FROM gwas_weights"
        diseases = fetch_all(query)
        
        results = {}
        for d in diseases:
            d_id = d["disease_id"]
            d_name = d["disease_name"]
            res = self.compute_disease_prs(d_id, user_dosages)
            res["disease_name"] = d_name
            results[d_id] = res
            
        return results

prs_engine = PRSEngine()
