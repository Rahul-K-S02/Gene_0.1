import os
import gzip
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "sample_vcf_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Standard VCF v4.2 Header
VCF_HEADER = """##fileformat=VCFv4.2
##fileDate=20260830
##source=GeneRiskGenomicsEngine_v2.0
##reference=GRCh38/hg38
##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE_001
"""

# 1. High CAD Profile
CAD_VARIANTS = [
    ("chr9", 22125503, "rs1333049", "C", "G", "1/1"),
    ("chr2", 21008099, "rs693", "A", "G", "1/1"),
    ("chr6", 160584488, "rs10455872", "A", "G", "0/1"),
    ("chr1", 55039983, "rs11591147", "G", "T", "0/0"),
    ("chr10", 112998590, "rs7903146", "C", "T", "0/1"),
    ("chr12", 21178615, "rs4149056", "T", "C", "0/1"),
    ("chr19", 44908684, "rs429358", "T", "C", "0/0"),
    ("chr19", 44908822, "rs7412", "C", "T", "0/0"),
]

# 2. Metabolic & Type 2 Diabetes Profile
T2D_VARIANTS = [
    ("chr10", 112998590, "rs7903146", "C", "T", "1/1"),
    ("chr11", 17409572, "rs5215", "G", "A", "1/1"),
    ("chr3", 12393125, "rs1801282", "C", "G", "0/0"),
    ("chr16", 53767014, "rs9939609", "T", "A", "1/1"),
    ("chr9", 22125503, "rs1333049", "C", "G", "0/0"),
    ("chr19", 44908684, "rs429358", "T", "C", "0/0"),
]

# 3. Pharmacogenomics Medication Sensitivity Profile
PGX_VARIANTS = [
    ("chr10", 94781859, "rs4244285", "G", "A", "0/1"), # CYP2C19 *2 Clopidogrel
    ("chr12", 21178615, "rs4149056", "T", "C", "0/1"), # SLCO1B1 *5 Simvastatin
    ("chr16", 31084274, "rs9923231", "C", "T", "0/1"), # VKORC1 Warfarin
    ("chr10", 94942293, "rs1057910", "A", "C", "0/1"), # CYP2C9 *3 Warfarin
    ("chr1", 97078894, "rs3918290", "C", "T", "0/0"),  # DPYD 5-FU
    ("chr9", 22125503, "rs1333049", "C", "G", "0/1"),
]

def build_vcf_text(variants):
    lines = [VCF_HEADER.strip()]
    for chrom, pos, rsid, ref, alt, gt in variants:
        line = f"{chrom}\t{pos}\t{rsid}\t{ref}\t{alt}\t99\tPASS\tAF=0.35\tGT:DP:GQ\t{gt}:30:99"
        lines.append(line)
    return "\n".join(lines) + "\n"

def generate_samples():
    profiles = [
        ("patient_cad_high_risk.vcf", CAD_VARIANTS),
        ("patient_t2d_metabolic.vcf", T2D_VARIANTS),
        ("patient_pharmgkb_statin_alert.vcf", PGX_VARIANTS),
    ]

    for filename, var_list in profiles:
        vcf_content = build_vcf_text(var_list)
        # Write plain .vcf
        out_vcf = OUTPUT_DIR / filename
        out_vcf.write_text(vcf_content, encoding="utf-8")
        print(f"[CREATED] {out_vcf}")

        # Write compressed .vcf.gz
        out_gz = OUTPUT_DIR / f"{filename}.gz"
        with gzip.open(out_gz, "wt", encoding="utf-8") as f:
            f.write(vcf_content)
        print(f"[CREATED] {out_gz}")

if __name__ == "__main__":
    generate_samples()
