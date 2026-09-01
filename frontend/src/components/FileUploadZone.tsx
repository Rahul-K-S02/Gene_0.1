'use client';

import React, { useState, useRef } from 'react';
import { streamAndParseVcfInBrowser } from '../lib/vcfChunkStreamer';
import { UploadCloud, FileText, CheckCircle2, Sparkles, RefreshCw, Dna, Download } from 'lucide-react';

interface FileUploadZoneProps {
  onGenomicDataReady: (data: Record<string, number>, fileName: string) => void;
  selectedFileName: string | null;
  onClearFile: () => void;
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({
  onGenomicDataReady,
  selectedFileName,
  onClearFile,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [progressPct, setProgressPct] = useState(0);
  const [statusText, setStatusText] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const processFile = async (file: File) => {
    // 1. Direct JSON file
    if (file.name.endsWith('.json')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const parsed = JSON.parse(e.target?.result as string);
          const genomicData = parsed.genomic_data || parsed;
          onGenomicDataReady(genomicData, file.name);
        } catch (err) {
          alert('Invalid JSON file format.');
        }
      };
      reader.readAsText(file);
      return;
    }

    // 2. Automated in-browser streaming for .vcf / .vcf.gz of ANY size
    setProcessing(true);
    setProgressPct(5);
    setStatusText('Starting automated in-browser genomic variant scanner...');

    try {
      const dosages = await streamAndParseVcfInBrowser(file, (pct, status) => {
        setProgressPct(pct);
        setStatusText(status);
      });

      onGenomicDataReady(dosages, `${file.name} (${Object.keys(dosages).length} Panel SNPs Detected)`);
    } catch (err: any) {
      console.error('In-browser streaming failed:', err);
      alert('Could not parse VCF file. Please check file format.');
    } finally {
      setProcessing(false);
      setProgressPct(0);
    }
  };

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
            <UploadCloud className="h-4 w-4" />
          </div>
          <h3 className="text-sm font-black uppercase tracking-wider text-slate-800">
            Automated Genomic VCF Upload
          </h3>
        </div>
        <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
          100% In-Browser Auto-Stream
        </span>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processFile(e.dataTransfer.files[0]);
          }
        }}
        onClick={() => !processing && fileInputRef.current?.click()}
        className={`relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-6 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-brand-500 bg-brand-50/50'
            : selectedFileName
            ? 'border-emerald-400 bg-emerald-50/30'
            : 'border-slate-300 bg-slate-50/50 hover:bg-slate-100 hover:border-slate-400'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".vcf,.vcf.gz,.gz,.json"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              processFile(e.target.files[0]);
            }
          }}
          className="hidden"
        />

        {processing ? (
          <div className="w-full py-4 space-y-3">
            <div className="flex justify-center">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-100 text-brand-600 animate-spin">
                <Dna className="h-5 w-5" />
              </div>
            </div>
            <div>
              <p className="text-xs font-bold text-slate-900">{statusText}</p>
              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-200 max-w-xs mx-auto">
                <div
                  style={{ width: `${progressPct}%` }}
                  className="h-full bg-brand-600 rounded-full transition-all duration-300"
                />
              </div>
            </div>
          </div>
        ) : selectedFileName ? (
          <div className="flex flex-col items-center space-y-2 py-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 shadow-2xs">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs font-black text-slate-900">{selectedFileName}</p>
              <p className="text-[11px] text-emerald-600 font-bold mt-0.5">
                Ready for multi-disease calculation
              </p>
            </div>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onClearFile();
              }}
              className="mt-1 text-[11px] font-bold text-rose-600 hover:underline"
            >
              Remove &amp; select another file
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center space-y-2 py-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-100 text-brand-600 shadow-2xs">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs sm:text-sm font-bold text-slate-800">
                Drag &amp; drop any <span className="text-brand-600">.vcf</span> or{' '}
                <span className="text-brand-600">.vcf.gz</span> file
              </p>
              <p className="text-[11px] text-slate-500 mt-1 max-w-xs mx-auto leading-relaxed">
                Small or multi-gigabyte whole-genome files are automatically parsed in your browser in seconds.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Download Real Sample VCF Files */}
      <div className="mt-4 border-t border-slate-100 pt-3">
        <span className="text-[11px] font-bold text-slate-500 block mb-1.5">
          Need a real benchmark VCF file to test? Download below:
        </span>
        <div className="flex flex-wrap gap-1.5">
          <a
            href={`${API_BASE_URL}/api/v1/download/sample-vcf/patient_cad_high_risk.vcf`}
            download
            className="inline-flex items-center space-x-1 rounded-lg bg-slate-100 hover:bg-brand-50 hover:text-brand-700 px-2.5 py-1 text-[10px] font-bold text-slate-700 border border-slate-200 transition-colors"
          >
            <Download className="h-3 w-3" />
            <span>High CAD (.vcf)</span>
          </a>
          <a
            href={`${API_BASE_URL}/api/v1/download/sample-vcf/patient_t2d_metabolic.vcf.gz`}
            download
            className="inline-flex items-center space-x-1 rounded-lg bg-slate-100 hover:bg-brand-50 hover:text-brand-700 px-2.5 py-1 text-[10px] font-bold text-slate-700 border border-slate-200 transition-colors"
          >
            <Download className="h-3 w-3" />
            <span>Diabetes (.vcf.gz)</span>
          </a>
          <a
            href={`${API_BASE_URL}/api/v1/download/sample-vcf/patient_pharmgkb_statin_alert.vcf`}
            download
            className="inline-flex items-center space-x-1 rounded-lg bg-slate-100 hover:bg-brand-50 hover:text-brand-700 px-2.5 py-1 text-[10px] font-bold text-slate-700 border border-slate-200 transition-colors"
          >
            <Download className="h-3 w-3" />
            <span>PharmGKB Alerts (.vcf)</span>
          </a>
        </div>
      </div>
    </div>
  );
};
