'use client';

import React from 'react';
import { PharmGKBAnnotation, ClinVarAnnotation } from '../lib/types';
import { Pill, ShieldAlert, AlertTriangle, ExternalLink, FileWarning } from 'lucide-react';

interface PharmGKBCardProps {
  pharmgkbAlerts: PharmGKBAnnotation[];
  clinvarFindings: ClinVarAnnotation[];
}

export const PharmGKBCard: React.FC<PharmGKBCardProps> = ({
  pharmgkbAlerts,
  clinvarFindings,
}) => {
  if (pharmgkbAlerts.length === 0 && clinvarFindings.length === 0) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center space-x-2 mb-4">
        <Pill className="h-5 w-5 text-purple-600" />
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Pharmacogenomics (PharmGKB) &amp; ClinVar Alerts
          </h3>
          <p className="text-xs text-slate-500">
            Actionable drug-gene metabolism interactions and high-penetrance pathogenic variants.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {/* PharmGKB Alerts */}
        {pharmgkbAlerts.map((pg, idx) => (
          <div
            key={idx}
            className="flex flex-col sm:flex-row sm:items-start justify-between rounded-xl border border-purple-200 bg-purple-50/50 p-4 gap-3"
          >
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-1.5">
                <span className="rounded-lg bg-purple-600 px-2.5 py-0.5 text-xs font-bold text-white">
                  {pg.drug}
                </span>
                <span className="text-xs font-bold text-purple-950">
                  Gene: <i>{pg.gene}</i> ({pg.rsid})
                </span>
                <span className="rounded-md bg-purple-200/70 px-2 py-0.5 text-[11px] font-semibold text-purple-900">
                  {pg.phenotype_category}
                </span>
                <span className="text-[10px] font-bold text-purple-700 uppercase bg-white border border-purple-200 px-1.5 py-0.5 rounded">
                  {pg.level_of_evidence}
                </span>
              </div>
              <p className="text-xs text-purple-900 leading-relaxed font-medium">
                {pg.clinical_recommendation}
              </p>
            </div>
          </div>
        ))}

        {/* ClinVar Pathogenic Findings */}
        {clinvarFindings.map((cv, idx) => (
          <div
            key={idx}
            className="flex flex-col sm:flex-row sm:items-start justify-between rounded-xl border border-rose-200 bg-rose-50/50 p-4 gap-3"
          >
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-1.5">
                <span className="rounded-lg bg-rose-600 px-2.5 py-0.5 text-xs font-bold text-white">
                  {cv.clinical_significance}
                </span>
                <span className="text-xs font-bold text-rose-950">
                  Gene: <i>{cv.gene}</i> ({cv.rsid})
                </span>
                <span className="text-[10px] text-rose-700 bg-white border border-rose-200 px-1.5 py-0.5 rounded font-mono">
                  {cv.accession}
                </span>
              </div>
              <p className="text-xs text-rose-900 leading-relaxed font-medium">
                Associated condition: <span className="font-bold">{cv.phenotype}</span>. Review Status: {cv.review_status}.
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
