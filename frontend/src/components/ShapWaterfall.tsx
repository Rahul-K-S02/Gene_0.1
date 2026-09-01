'use client';

import React, { useState } from 'react';
import { DiseaseRiskResult } from '../lib/types';
import { BarChart3, Image as ImageIcon, Sparkles, AlertCircle, Info } from 'lucide-react';

interface ShapWaterfallProps {
  disease: DiseaseRiskResult;
}

export const ShapWaterfall: React.FC<ShapWaterfallProps> = ({ disease }) => {
  const [viewMode, setViewMode] = useState<'chart' | 'plot'>('chart');

  const items = Object.entries(disease.shap_feature_importance || {}).sort(
    (a, b) => Math.abs(b[1]) - Math.abs(a[1])
  );

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-brand-600" />
            <h3 className="text-base font-bold text-slate-900">
              SHAP Explainability &amp; Feature Attribution — {disease.disease_name}
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Exact Shapley values measuring each feature&apos;s push toward higher risk (+) or protection (-).
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {/* Mode Badge */}
          <span
            className={`rounded-full px-3 py-1 text-xs font-bold border ${
              disease.shap_mode === 'real_shap'
                ? 'bg-indigo-50 text-indigo-700 border-indigo-200'
                : 'bg-slate-100 text-slate-700 border-slate-300'
            }`}
          >
            {disease.shap_mode === 'real_shap' ? 'Real TreeExplainer SHAP' : 'Approximate Linear'}
          </span>

          {/* Toggle between custom chart & backend plot */}
          {disease.shap_waterfall_plot_b64 && (
            <div className="flex rounded-lg border border-slate-200 bg-slate-50 p-0.5 text-xs">
              <button
                type="button"
                onClick={() => setViewMode('chart')}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  viewMode === 'chart'
                    ? 'bg-white font-bold text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Interactive
              </button>
              <button
                type="button"
                onClick={() => setViewMode('plot')}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  viewMode === 'plot'
                    ? 'bg-white font-bold text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Matplotlib Plot
              </button>
            </div>
          )}
        </div>
      </div>

      {viewMode === 'plot' && disease.shap_waterfall_plot_b64 ? (
        <div className="flex flex-col items-center rounded-xl bg-slate-50 p-3 border border-slate-200">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={disease.shap_waterfall_plot_b64}
            alt="SHAP Waterfall Plot"
            className="max-h-[380px] w-auto rounded-lg shadow-xs"
          />
          <span className="text-[11px] text-slate-400 mt-2">
            In-memory server-rendered SHAP force waterfall plot
          </span>
        </div>
      ) : (
        <div className="space-y-2.5">
          {items.map(([feature, val]) => {
            const isRisk = val > 0;
            const maxVal = Math.max(...items.map(([, v]) => Math.abs(v)), 0.5);
            const widthPct = Math.min(100, Math.max(8, (Math.abs(val) / maxVal) * 100));

            return (
              <div
                key={feature}
                className="flex items-center justify-between rounded-xl bg-slate-50/70 p-3 border border-slate-100"
              >
                <div className="w-1/3 min-w-[140px]">
                  <span className="text-xs font-bold text-slate-800 block">{feature}</span>
                  <span className="text-[10px] text-slate-400">
                    {isRisk ? 'Increases risk' : 'Protective factor'}
                  </span>
                </div>

                <div className="flex-1 px-4">
                  <div className="flex h-3 w-full items-center rounded-full bg-slate-200 overflow-hidden">
                    <div
                      style={{ width: `${widthPct}%` }}
                      className={`h-full rounded-full transition-all ${
                        isRisk ? 'bg-rose-500' : 'bg-emerald-500'
                      }`}
                    />
                  </div>
                </div>

                <div className="w-16 text-right">
                  <span
                    className={`text-xs font-black ${
                      isRisk ? 'text-rose-600' : 'text-emerald-600'
                    }`}
                  >
                    {isRisk ? `+${val.toFixed(2)}` : val.toFixed(2)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Key Drivers Callout */}
      {disease.key_risk_drivers && disease.key_risk_drivers.length > 0 && (
        <div className="mt-4 rounded-xl bg-amber-50/60 border border-amber-200/80 p-3 text-xs">
          <div className="flex items-center space-x-1.5 font-bold text-amber-900 mb-1">
            <Info className="h-4 w-4 text-amber-600" />
            <span>Key Identified Signals for {disease.disease_name}:</span>
          </div>
          <ul className="list-disc list-inside space-y-0.5 text-amber-800 text-[11px] font-medium">
            {disease.key_risk_drivers.map((drv, i) => (
              <li key={i}>{drv}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
