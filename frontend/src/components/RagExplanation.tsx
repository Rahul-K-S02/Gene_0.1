'use client';

import React from 'react';
import { Sparkles, FileDown, MessageSquareQuote, BookOpen, CheckCircle, ExternalLink, Play } from 'lucide-react';
import { FormattedMessage } from './FormattedMessage';

interface CitationItem {
  title: string;
  citation: string;
  url?: string;
  video_url?: string;
  pmid?: string;
}

interface RagExplanationProps {
  narrative: string;
  prescriptions: string[];
  citations: CitationItem[];
  pdfBase64?: string;
  onOpenChat: () => void;
}

export const RagExplanation: React.FC<RagExplanationProps> = ({
  narrative,
  prescriptions,
  citations,
  pdfBase64,
  onOpenChat,
}) => {
  const handleDownloadPdf = () => {
    if (!pdfBase64) return;
    const link = document.createElement('a');
    link.href = `data:application/pdf;base64,${pdfBase64}`;
    link.download = `GeneRisk_Clinical_Report_${new Date().toISOString().slice(0, 10)}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-5 gap-3">
        <div className="flex items-center space-x-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-100 text-brand-700">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Evidence-Grounded Clinical Genomic Evaluation
            </h3>
            <p className="text-xs text-slate-500">
              Synthesized by GeneRisk RAG engine &amp; grounded in peer-reviewed guidelines.
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2.5">
          <button
            type="button"
            onClick={onOpenChat}
            className="flex items-center space-x-1.5 rounded-xl border border-brand-200 bg-brand-50 px-3.5 py-2 text-xs font-bold text-brand-700 hover:bg-brand-100 transition-colors shadow-xs"
          >
            <MessageSquareQuote className="h-4 w-4" />
            <span>Ask Report Questions</span>
          </button>

          {pdfBase64 && (
            <button
              type="button"
              onClick={handleDownloadPdf}
              className="flex items-center space-x-1.5 rounded-xl bg-slate-900 px-3.5 py-2 text-xs font-bold text-white hover:bg-slate-800 transition-colors shadow-xs"
            >
              <FileDown className="h-4 w-4 text-brand-400" />
              <span>Download PDF</span>
            </button>
          )}
        </div>
      </div>

      {/* Narrative Body */}
      <div className="rounded-xl bg-slate-50 p-4 border border-slate-200 text-xs text-slate-700 leading-relaxed mb-5">
        <FormattedMessage content={narrative} />
      </div>

      {/* Actionable Prescriptions */}
      {prescriptions && prescriptions.length > 0 && (
        <div className="mb-5">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-2.5">
            Personalized Clinical Risk-Reduction Prescriptions
          </span>
          <div className="space-y-2">
            {prescriptions.map((rx, idx) => (
              <div
                key={idx}
                className="flex items-start space-x-2.5 rounded-xl bg-emerald-50/70 border border-emerald-200 p-3 text-xs text-emerald-950"
              >
                <CheckCircle className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                <span className="font-medium leading-relaxed">{rx}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Grounding Literature Citations */}
      {citations && citations.length > 0 && (
        <div className="border-t border-slate-100 pt-4">
          <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-600 mb-2">
            <BookOpen className="h-3.5 w-3.5 text-slate-400" />
            <span>Retrieved Clinical Evidence Sources (Qdrant RAG):</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {citations.map((c, i) => (
              <div
                key={i}
                className="rounded-xl bg-slate-50 border border-slate-200/80 p-3 text-[11px] text-slate-600 flex flex-col justify-between"
              >
                <div>
                  <p className="font-bold text-slate-800">{c.title}</p>
                  <p className="text-slate-500 italic mt-0.5">{c.citation}</p>
                </div>
                <div className="flex items-center space-x-3 pt-2 mt-2 border-t border-slate-200/60 text-[10px]">
                  {c.url && (
                    <a
                      href={c.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brand-600 hover:text-brand-800 font-bold inline-flex items-center space-x-1"
                    >
                      <span>Read Literature</span>
                      <ExternalLink className="h-2.5 w-2.5" />
                    </a>
                  )}
                  {c.video_url && (
                    <a
                      href={c.video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-rose-600 hover:text-rose-800 font-bold inline-flex items-center space-x-1"
                    >
                      <Play className="h-2.5 w-2.5 fill-current" />
                      <span>Watch Video</span>
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
