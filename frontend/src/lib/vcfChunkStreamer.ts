import * as pako from 'pako';
import { TARGET_COORDINATE_MAP } from './vcfCoordinatesMap';
import { SUPPORTED_TARGET_RSIDS } from './supportedRsids';

function parseGenotype(gtStr: string): number | null {
  if (!gtStr || gtStr === './.' || gtStr === '.|.' || gtStr === '.') return null;
  const fields = gtStr.split(':');
  const gt = fields[0].replace(/\|/g, '/');
  const alleles = gt.split('/');
  if (alleles.length === 2) {
    const a1 = parseInt(alleles[0], 10);
    const a2 = parseInt(alleles[1], 10);
    if (!isNaN(a1) && !isNaN(a2)) {
      return (a1 > 0 ? 1 : 0) + (a2 > 0 ? 1 : 0);
    }
  } else if (alleles.length === 1) {
    const a1 = parseInt(alleles[0], 10);
    if (!isNaN(a1)) return a1 > 0 ? 1.0 : 0.0;
  }
  return null;
}

function resolveRsidOrCoordinate(parts: string[]): string | null {
  // 1. Check if ID column has a direct rsID match
  const rawId = parts[2]?.trim();
  if (rawId && SUPPORTED_TARGET_RSIDS.has(rawId)) {
    return rawId;
  }

  // 2. Fallback: match by chromosomal coordinate (supports GIAB, WGS with ID=".")
  const chrom = parts[0]?.trim().toLowerCase().replace('chr', '');
  const pos = parts[1]?.trim();
  if (chrom && pos) {
    const coordKey = `${chrom}:${pos}`;
    const matchedRsid = TARGET_COORDINATE_MAP[coordKey];
    if (matchedRsid) {
      return matchedRsid;
    }
  }

  return null;
}

export async function streamAndParseVcfInBrowser(
  file: File,
  onProgress?: (progressPct: number, statusText: string) => void
): Promise<Record<string, number>> {
  const isGzipped = file.name.endsWith('.gz');
  const extractedDosages: Record<string, number> = {};

  if (isGzipped) {
    onProgress?.(15, 'Decompressing and scanning genomic variants in browser memory...');
    const buffer = await file.arrayBuffer();
    onProgress?.(40, 'Inflating compressed gzip stream...');
    
    let text = '';
    try {
      const decompressed = pako.ungzip(new Uint8Array(buffer));
      text = new TextDecoder('utf-8').decode(decompressed);
    } catch (e) {
      text = new TextDecoder('utf-8').decode(buffer);
    }

    onProgress?.(70, 'Scanning SNP panel variants & loci coordinates...');
    const lines = text.split('\n');
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.startsWith('#')) continue;
      const parts = line.trim().split('\t');
      if (parts.length < 10) continue;

      const matchedRsid = resolveRsidOrCoordinate(parts);
      if (matchedRsid) {
        const formatKeys = parts[8]?.split(':') || [];
        const sampleVals = parts[9]?.split(':') || [];
        let gtVal = sampleVals[0];
        const gtIdx = formatKeys.indexOf('GT');
        if (gtIdx !== -1 && gtIdx < sampleVals.length) {
          gtVal = sampleVals[gtIdx];
        }

        const dosage = parseGenotype(gtVal);
        if (dosage !== null) {
          extractedDosages[matchedRsid] = dosage;
        }
      }
    }
    onProgress?.(100, `Complete! Extracted ${Object.keys(extractedDosages).length} panel SNPs.`);
    return extractedDosages;
  }

  // Plain Text Chunk Streaming
  const chunkSize = 1024 * 1024 * 2; // 2MB chunks
  let offset = 0;
  const fileSize = file.size;
  let leftover = '';

  while (offset < fileSize) {
    const slice = file.slice(offset, offset + chunkSize);
    const textChunk = await slice.text();
    const fullChunk = leftover + textChunk;
    const lines = fullChunk.split('\n');
    leftover = lines.pop() || '';

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.startsWith('#')) continue;
      const parts = line.trim().split('\t');
      if (parts.length < 10) continue;

      const matchedRsid = resolveRsidOrCoordinate(parts);
      if (matchedRsid) {
        const formatKeys = parts[8]?.split(':') || [];
        const sampleVals = parts[9]?.split(':') || [];
        let gtVal = sampleVals[0];
        const gtIdx = formatKeys.indexOf('GT');
        if (gtIdx !== -1 && gtIdx < sampleVals.length) {
          gtVal = sampleVals[gtIdx];
        }

        const dosage = parseGenotype(gtVal);
        if (dosage !== null) {
          extractedDosages[matchedRsid] = dosage;
        }
      }
    }

    offset += chunkSize;
    const pct = Math.min(98, Math.round((offset / fileSize) * 100));
    onProgress?.(pct, `Scanning genomic loci... (${pct}%)`);
  }

  onProgress?.(100, `Extraction complete! Found ${Object.keys(extractedDosages).length} target variants.`);
  return extractedDosages;
}
