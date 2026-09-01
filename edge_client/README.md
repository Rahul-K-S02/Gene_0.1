# GeneRisk Standalone Edge Preprocessing Tool

`generisk_edge.py` is a zero-dependency, pure Python 3 standard library CLI tool designed to handle whole-genome sequencing (WGS) and whole-exome sequencing (WES) VCF files of arbitrary size (from 100MB up to 25GB+).

---

## Why Edge Preprocessing?

Browser-based uploads of 13–25GB VCF files fail due to network timeouts, browser tab memory ceilings, and server RAM limits. Furthermore, uploading raw genome sequence data exposes unneeded private genomic information over the wire.

`generisk_edge.py` solves this by:
1. **Streaming line-by-line in $O(1)$ memory** (<30MB RAM overhead).
2. **Filtering directly against the live GeneRisk SNP panel**.
3. **Extracting only numeric allele dosages (0, 1, 2) without storing raw DNA sequences**.
4. **Generating an inspectable, tiny JSON file (<50 KB)** that uploads in milliseconds.

---

## Quick Start

No virtual environment or `pip install` is required — it runs with standard Python 3.7+:

```bash
# 1. Run on a plain .vcf or compressed .vcf.gz file
python generisk_edge.py my_genome.vcf.gz

# 2. Specify a custom backend server address
python generisk_edge.py my_genome.vcf.gz --api-url https://generisk-backend.onrender.com

# 3. Specify custom output destination
python generisk_edge.py my_genome.vcf.gz -o filtered_dosages.json
```

Once processed, simply upload the resulting `.json` file into the GeneRisk web interface or use the API.
