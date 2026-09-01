'use client';

import React from 'react';
import { DemoSample } from '../lib/types';
import { Sparkles, HeartPulse, Dna, Pill, ShieldCheck, Activity } from 'lucide-react';

interface DemoPresetSelectorProps {
  samples: DemoSample[];
  selectedId: string | null;
  onSelectSample: (sample: DemoSample) => void;
}

export const DemoPresetSelector: React.FC<DemoPresetSelectorProps> = ({
  samples,
  selectedId,
  onSelectSample,
}) => {
  const getIcon = (id: string) => {
    if (id.includes('cad')) return <HeartPulse className="h-5 w-5 text-rose-500" />;
    if (id.includes('t2d')) return <Dna className="h-5 w-5 text-amber-500" />;
    if (id.includes('healthy')) return <ShieldCheck className="h-5 w-5 text-emerald-500" />;
    if (id.includes('pgx')) return <Pill className="h-5 w-5 text-purple-500" />;
    return <Activity className="h-5 w-5 text-brand-500" />;
  };

  const getBadgeColor = (id: string) => {
    if (id.includes('cad')) return 'bg-rose-100 text-rose-800 border-rose-200';
    if (id.includes('t2d')) return 'bg-amber-100 text-amber-800 border-amber-200';
    if (id.includes('healthy')) return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (id.includes('pgx')) return 'bg-purple-100 text-purple-800 border-purple-200';
    return 'bg-blue-100 text-blue-800 border-blue-200';
  };

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center space-x-2 mb-2">
        <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-brand-100 text-brand-600">
          <Sparkles className="h-3.5 w-3.5" />
        </div>
        <h3 className="text-sm font-black uppercase tracking-wider text-slate-800">
          Instant 1-Click Patient Profiles (For Quick Testing)
        </h3>
      </div>
      <p className="text-xs text-slate-500 mb-4 font-normal">
        Don&apos;t have a VCF file? Pick an everyday example profile below to instantly see how genes and lifestyle combine into risk scores.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {samples.map((sample) => {
          const isSelected = selectedId === sample.id;
          return (
            <button
              key={sample.id}
              onClick={() => onSelectSample(sample)}
              className={`flex flex-col justify-between p-4 rounded-2xl text-left border transition-all ${
                isSelected
                  ? 'border-brand-500 bg-brand-50/70 shadow-sm ring-2 ring-brand-500/20'
                  : 'border-slate-200 bg-slate-50/60 hover:bg-slate-100 hover:border-slate-300'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="p-1.5 rounded-xl bg-white shadow-2xs border border-slate-100">
                    {getIcon(sample.id)}
                  </div>
                  {sample.tag && (
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getBadgeColor(sample.id)}`}>
                      {sample.tag}
                    </span>
                  )}
                </div>

                <span className="text-xs font-black text-slate-900 leading-tight block mb-1">
                  {sample.title}
                </span>
                <p className="text-[11px] text-slate-600 line-clamp-3 leading-relaxed">
                  {sample.description}
                </p>
              </div>

              <span className="mt-3 text-[10px] font-bold text-brand-600 uppercase tracking-wider">
                Click to load profile &rarr;
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
