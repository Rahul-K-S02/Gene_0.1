'use client';

import React from 'react';
import { Terminal, Download, X, ShieldCheck, Zap, HardDrive, Check } from 'lucide-react';

interface EdgeToolModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const EdgeToolModal: React.FC<EdgeToolModalProps> = ({ isOpen, onClose }) => {
  const [copied, setCopied] = React.useState(false);

  if (!isOpen) return null;

  const commandText = 'python generisk_edge.py your_genome.vcf.gz';

  const handleCopy = () => {
    navigator.clipboard.writeText(commandText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    window.open(`${apiUrl}/download/edge-tool`, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
      <div className="flex flex-col w-full max-w-xl rounded-2xl bg-white shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-5 py-4">
          <div className="flex items-center space-x-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white shadow-xs">
              <Terminal className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                GeneRisk Edge Preprocessor (Zero-RAM CLI)
              </h3>
              <p className="text-[11px] text-slate-500 font-medium">
                Stream 13GB–25GB Whole-Genome VCFs in Constant Memory
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-200/60 hover:text-slate-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 space-y-4 text-xs text-slate-700">
          {/* Key Advantages */}
          <div className="grid grid-cols-3 gap-3">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-center">
              <HardDrive className="h-4 w-4 text-brand-600 mx-auto mb-1" />
              <span className="font-bold text-slate-900 block">&lt;30 MB RAM</span>
              <span className="text-[10px] text-slate-500">Streams any file size</span>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-center">
              <ShieldCheck className="h-4 w-4 text-emerald-600 mx-auto mb-1" />
              <span className="font-bold text-slate-900 block">100% Private</span>
              <span className="text-[10px] text-slate-500">Raw DNA never uploaded</span>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-center">
              <Zap className="h-4 w-4 text-amber-600 mx-auto mb-1" />
              <span className="font-bold text-slate-900 block">&lt;50 KB JSON</span>
              <span className="text-[10px] text-slate-500">Upload in 50ms</span>
            </div>
          </div>

          <p className="leading-relaxed">
            Uploading 13–25GB whole-genome VCF files through a web browser is prone to network failure, tab crashes, and privacy concerns. The standalone <code className="bg-slate-100 text-brand-700 px-1.5 py-0.5 rounded font-mono font-bold">generisk_edge.py</code> script runs locally on your machine with <strong>zero external dependencies</strong> (standard Python library only).
          </p>

          {/* Quick Steps */}
          <div className="rounded-xl bg-slate-900 p-4 text-slate-200 space-y-2.5 font-mono text-[11px]">
            <p className="text-slate-400"># 1. Download generisk_edge.py</p>
            <p className="text-slate-400"># 2. Run locally on your VCF or VCF.GZ file:</p>
            <div className="flex items-center justify-between bg-slate-800/80 rounded-lg p-2 border border-slate-700">
              <span className="text-emerald-400">{commandText}</span>
              <button
                onClick={handleCopy}
                className="flex items-center space-x-1 rounded bg-slate-700 hover:bg-slate-600 px-2 py-1 text-[10px] text-white transition-colors"
              >
                {copied ? <Check className="h-3 w-3 text-emerald-400" /> : null}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
            <p className="text-slate-400">
              # 3. Drag the resulting <span className="text-brand-300">generisk_filtered_panel.json</span> back into GeneRisk!
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 p-4">
          <span className="text-[11px] text-slate-500 font-medium">
            Requires standard Python 3.7+ (no pip installs)
          </span>
          <button
            type="button"
            onClick={handleDownload}
            className="flex items-center space-x-1.5 rounded-xl bg-brand-600 px-4 py-2 text-xs font-bold text-white hover:bg-brand-700 transition-colors shadow-xs"
          >
            <Download className="h-4 w-4" />
            <span>Download generisk_edge.py</span>
          </button>
        </div>
      </div>
    </div>
  );
};
