#!/usr/bin/env python3
"""
GeneRisk Standalone Edge Preprocessing Tool
===========================================
A zero-dependency, standard-library-only CLI utility that streams arbitrary-size 
Genomic VCF files (plain .vcf or bgzipped .vcf.gz) in constant memory (<30MB RAM).

It queries the live GeneRisk API to retrieve the current supported SNP panel,
extracts ONLY rsID dosages without storing or transmitting raw genetic sequences,
and produces a compact JSON payload (<50KB) that can be inspected and uploaded.

Usage:
    python generisk_edge.py path/to/sample.vcf.gz
    python generisk_edge.py sample.vcf.gz --api-url http://localhost:8000
    python generisk_edge.py sample.vcf --output my_genomics.json
"""

import sys
import os
import gzip
import json
import argparse
import urllib.request
import urllib.error
from typing import Set, Dict, Optional

# Default fallback rsIDs if offline/unreachable
FALLBACK_PANEL_RSIDS = {
    "rs1333049", "rs693", "rs10455872", "rs11591147", "rs20455",
    "rs7903146", "rs5215", "rs1801282", "rs9939609", "rs10811661",
    "rs429358", "rs7412", "rs11136000", "rs3818361", "rs744373",
    "rs699", "rs1799983", "rs5186", "rs11730589", "rs2384550",
    "rs2981582", "rs3803662", "rs889312", "rs13281615", "rs4970834",
    "rs4244285", "rs4149056", "rs9923231", "rs1057910", "rs3918290"
}

def fetch_panel_from_api(api_url: str) -> Set[str]:
    """Fetches the active panel rsIDs from the live GeneRisk server."""
    endpoint = f"{api_url.rstrip('/')}/api/v1/supported-panel"
    print(f"[Edge Tool] Querying live panel from: {endpoint} ...")
    try:
        req = urllib.request.Request(
            endpoint,
            headers={"User-Agent": "GeneRisk-EdgeClient/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                rsids = {item["rsid"] for item in data if "rsid" in item}
                print(f"[Edge Tool] Successfully retrieved {len(rsids)} target SNPs from live server.")
                return rsids
    except Exception as ex:
        print(f"[Edge Tool] Notice: Live API connection ({ex}) unavailable. Utilizing built-in default panel.")
    return FALLBACK_PANEL_RSIDS

def parse_genotype(gt_str: str) -> Optional[float]:
    """Converts VCF genotype string to alternate allele dosage (0.0, 1.0, 2.0)."""
    if not gt_str or gt_str in ("./.", ".|.", "."):
        return None
    fields = gt_str.split(":")
    gt = fields[0].replace("|", "/")
    alleles = gt.split("/")
    if len(alleles) == 2:
        try:
            a1, a2 = int(alleles[0]), int(alleles[1])
            return float((1 if a1 > 0 else 0) + (1 if a2 > 0 else 0))
        except ValueError:
            return None
    elif len(alleles) == 1:
        try:
            return 1.0 if int(alleles[0]) > 0 else 0.0
        except ValueError:
            return None
    return None

def stream_vcf_and_extract(file_path: str, target_rsids: Set[str]) -> Dict[str, float]:
    """
    Streams a VCF line-by-line in O(1) memory, extracting target variants.
    """
    if not os.path.exists(file_path):
        print(f"[Error] File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    is_gz = file_path.endswith(".gz")
    open_func = gzip.open if is_gz else open
    mode = "rt" if is_gz else "r"

    extracted: Dict[str, float] = {}
    line_count = 0
    match_count = 0

    print(f"[Edge Tool] Streaming {file_path} (Format: {'GZIP' if is_gz else 'PLAIN TEXT'})...")
    
    with open_func(file_path, mode, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_count += 1
            if line_count % 500000 == 0:
                print(f"  ... processed {line_count:,} lines (extracted {match_count} SNPs) ...")

            if line.startswith("#"):
                continue

            # Tab-delimited split
            parts = line.strip().split("\t")
            if len(parts) < 10:
                continue

            rsid = parts[2].strip()
            if rsid in target_rsids:
                format_col = parts[8]
                sample_col = parts[9]
                
                format_keys = format_col.split(":")
                sample_vals = sample_col.split(":")
                
                gt_val = None
                if "GT" in format_keys:
                    idx = format_keys.index("GT")
                    if idx < len(sample_vals):
                        gt_val = sample_vals[idx]
                elif len(sample_vals) > 0:
                    gt_val = sample_vals[0]

                if gt_val:
                    dosage = parse_genotype(gt_val)
                    if dosage is not None:
                        extracted[rsid] = dosage
                        match_count += 1

    print(f"[Edge Tool] Complete! Scanned {line_count:,} total lines. Extracted {len(extracted)} panel variants.")
    return extracted

def main():
    parser = argparse.ArgumentParser(
        description="GeneRisk Edge Client: Ultra-lightweight streaming VCF variant extractor."
    )
    parser.add_argument("vcf_file", help="Path to input .vcf or .vcf.gz file")
    parser.add_argument(
        "--api-url", 
        default="http://localhost:8000",
        help="GeneRisk backend API URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--output", "-o",
        default="generisk_filtered_panel.json",
        help="Output JSON file destination (default: generisk_filtered_panel.json)"
    )
    
    args = parser.parse_args()
    
    # 1. Fetch panel
    target_rsids = fetch_panel_from_api(args.api_url)
    
    # 2. Stream and extract
    dosages = stream_vcf_and_extract(args.vcf_file, target_rsids)
    
    # 3. Write output JSON
    payload = {
        "generator": "GeneRisk Edge Preprocessor v1.0",
        "variants_count": len(dosages),
        "genomic_data": dosages
    }
    
    with open(args.output, "w", encoding="utf-8") as out:
        json.dump(payload, out, indent=2)

    file_size_kb = os.path.getsize(args.output) / 1024.0
    print(f"\n[Success] Output written to: {args.output} ({file_size_kb:.1f} KB)")
    print("[Privacy Notice] Raw sequence letters were never stored or transmitted. You may safely upload this small JSON file to GeneRisk.")

if __name__ == "__main__":
    main()
