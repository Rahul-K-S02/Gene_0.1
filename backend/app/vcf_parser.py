import os
import gzip
import logging
from pathlib import Path
from typing import Dict, Set, Optional, Tuple

logger = logging.getLogger("generisk.vcf_parser")

def parse_genotype_to_dosage(gt_str: str) -> Optional[float]:
    """
    Parses VCF genotype string (e.g., '0/0', '0/1', '1/1', '0|1', '1|1', './.')
    into numeric alternate allele dosage (0.0, 1.0, 2.0).
    """
    if not gt_str or gt_str in ("./.", ".|.", "."):
        return None
    
    # Check if there are colon-separated fields (GT:DS:GP)
    fields = gt_str.split(":")
    gt = fields[0]
    
    # Check for direct DS dosage field if available
    if len(fields) > 1:
        for f in fields[1:]:
            try:
                ds_val = float(f)
                if 0.0 <= ds_val <= 2.0:
                    return ds_val
            except ValueError:
                pass

    # Parse GT alleles
    alleles = gt.replace("|", "/").split("/")
    if len(alleles) == 2:
        try:
            a1, a2 = int(alleles[0]), int(alleles[1])
            # Count alternate alleles
            return float((1 if a1 > 0 else 0) + (1 if a2 > 0 else 0))
        except ValueError:
            return None
    elif len(alleles) == 1:
        # Hemizygous (e.g. male chrX / chrY)
        try:
            return 1.0 if int(alleles[0]) > 0 else 0.0
        except ValueError:
            return None

    return None

def parse_vcf_stream(
    file_path: Path, 
    target_rsids: Optional[Set[str]] = None,
    delete_after: bool = True
) -> Dict[str, float]:
    """
    Stream-parses a VCF file (plain or .gz), extracting ONLY target rsIDs and dosage.
    Ensures zero disk persistence: deletes the file immediately upon completion.
    """
    dosages: Dict[str, float] = {}
    is_gzipped = str(file_path).endswith(".gz")
    
    try:
        open_fn = gzip.open if is_gzipped else open
        mode = "rt" if is_gzipped else "r"
        
        with open_fn(file_path, mode, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                
                parts = line.strip().split("\t")
                if len(parts) < 10:
                    continue
                
                rsid = parts[2].strip()
                if not rsid.startswith("rs"):
                    continue
                
                if target_rsids is not None and rsid not in target_rsids:
                    continue
                
                format_col = parts[8]
                sample_col = parts[9]
                
                format_keys = format_col.split(":")
                sample_vals = sample_col.split(":")
                
                gt_val = None
                if "GT" in format_keys:
                    gt_idx = format_keys.index("GT")
                    if gt_idx < len(sample_vals):
                        gt_val = sample_vals[gt_idx]
                elif len(sample_vals) > 0:
                    gt_val = sample_vals[0]
                
                if gt_val:
                    dosage = parse_genotype_to_dosage(gt_val)
                    if dosage is not None:
                        dosages[rsid] = dosage
                        
        logger.info(f"Successfully extracted {len(dosages)} target SNPs from VCF.")
    except Exception as e:
        logger.error(f"Error parsing VCF {file_path}: {e}")
        raise
    finally:
        if delete_after and file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Ephemeral file {file_path} deleted immediately.")
            except Exception as ex:
                logger.warning(f"Could not delete temporary file {file_path}: {ex}")

    return dosages

def clean_genomic_input(genomic_data: Optional[Dict[str, float]]) -> Dict[str, float]:
    """
    Validates and standardizes a genomic dictionary mapping rsID to dosage.
    """
    if not genomic_data:
        return {}
    
    cleaned = {}
    for rsid, dosage in genomic_data.items():
        if isinstance(rsid, str) and rsid.startswith("rs"):
            try:
                d = float(dosage)
                cleaned[rsid.strip()] = min(2.0, max(0.0, d))
            except (ValueError, TypeError):
                continue
    return cleaned
