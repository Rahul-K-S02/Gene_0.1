'use client';

import React from 'react';
import { DiseaseRiskResult } from '../lib/types';
import { ShieldCheck, AlertTriangle, ShieldAlert, HeartPulse, Info, CheckCircle2 } from 'lucide-react';

interface RiskOverviewCardProps {
  diseaseRisks: DiseaseRiskResult[];
  selectedDiseaseId: string;
  onSelectDisease: (diseaseId: string) => void;
}

export const RiskOverviewCard: React.FC<RiskOverviewCardProps> = ({
  diseaseRisks,
  selectedDiseaseId,
  onSelectDisease,
}) => {
  const getBadgeStyle = (category: string) => {
    switch (category) {
      case 'Low':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'Average':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'Elevated':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'High':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-300';
    }
  };

  const getPercentileColor = (percentile: number) => {
    if (percentile >= 80) return 'text-rose-600';
    if (percentile >= 60) return 'text-amber-600';
    if (percentile <= 25) return 'text-emerald-600';
    return 'text-blue-600';
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-slate-900">
            Multi-Disease Polygenic Risk &amp; Late-Fusion Overview
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Click on any condition to view detailed SHAP waterfall plots, bell curves, and what-if simulations.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {diseaseRisks.map((d) => {
          const isSelected = selectedDiseaseId === d.disease_id;
          return (
            <div
              key={d.disease_id}
              onClick={() => onSelectDisease(d.disease_id)}
              className={`flex flex-col justify-between p-4 rounded-xl border cursor-pointer transition-all ${
                isSelected
                  ? 'border-brand-500 bg-brand-50/40 shadow-sm ring-2 ring-brand-500/20'
                  : 'border-slate-200 bg-slate-50/50 hover:bg-slate-100 hover:border-slate-300'
              }`}
            >
              {/* Header: Title & Risk Category */}
              <div>
                <div className="flex items-start justify-between mb-2">
                  <span className="text-sm font-bold text-slate-900 leading-tight">
                    {d.disease_name}
                  </span>
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-xs font-bold border ${getBadgeStyle(
                      d.risk_category
                    )}`}
                  >
                    {d.risk_category}
                  </span>
                </div>

                {/* Risk Metrics */}
                <div className="grid grid-cols-2 gap-2 my-3 rounded-lg bg-white p-2.5 border border-slate-100 shadow-xs">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">
                      PRS Percentile
                    </span>
                    <span className={`text-base font-extrabold ${getPercentileColor(d.prs_percentile)}`}>
                      {d.prs_percentile.toFixed(1)}
                      <span className="text-xs font-medium text-slate-500">th %ile</span>
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">
                      10-Yr Absolute Risk
                    </span>
                    <span className="text-base font-extrabold text-slate-900">
                      {(d.fused_absolute_risk_10yr * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                {/* Genetics vs Lifestyle Proportion Bar */}
                <div className="mb-2">
                  <div className="flex justify-between text-[11px] font-semibold text-slate-600 mb-1">
                    <span>Genetics: {d.genetic_contribution_pct.toFixed(0)}%</span>
                    <span>Lifestyle: {d.lifestyle_contribution_pct.toFixed(0)}%</span>
                  </div>
                  <div className="flex h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
                    <div
                      style={{ width: `${d.genetic_contribution_pct}%` }}
                      className="bg-indigo-500"
                    />
                    <div
                      style={{ width: `${d.lifestyle_contribution_pct}%` }}
                      className="bg-emerald-500"
                    />
                  </div>
                </div>
              </div>

              {/* Footer: SNP Confidence & Explainability Mode */}
              <div className="mt-3 pt-2.5 border-t border-slate-200/70 flex items-center justify-between text-[11px] text-slate-500">
                <span className="flex items-center space-x-1" title="Analyzed panel SNPs">
                  <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                  <span>
                    {d.snps_found}/{d.snps_total} SNPs ({Math.round(d.confidence_score * 100)}%)
                  </span>
                </span>

                <span
                  className="font-medium text-[10px] rounded px-1.5 py-0.5 bg-slate-200/70 text-slate-700"
                  title="Explainability Engine"
                >
                  {d.shap_mode === 'real_shap' ? 'Real SHAP' : 'Approx Linear'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
