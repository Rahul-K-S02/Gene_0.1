'use client';

import React, { useState, useEffect } from 'react';
import { GovtScheme } from '../lib/types';
import { fetchGovtSchemes } from '../lib/api';
import { Landmark, ShieldCheck, Pill, Phone, ExternalLink, Globe, CheckCircle2, Search, Building2, MapPin } from 'lucide-react';

interface GovtSchemesSectionProps {
  currentLang: string;
}

export const GovtSchemesSection: React.FC<GovtSchemesSectionProps> = ({ currentLang }) => {
  const [selectedLang, setSelectedLang] = useState<string>(currentLang || 'en');
  const [schemes, setSchemes] = useState<GovtScheme[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedScheme, setSelectedScheme] = useState<GovtScheme | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>('all');

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await fetchGovtSchemes(selectedLang);
        setSchemes(data);
        if (data.length > 0) setSelectedScheme(data[0]);
      } catch (err) {
        console.error('Failed to load schemes:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [selectedLang]);

  const filtered = schemes.filter((s) => {
    if (filterCategory === 'all') return true;
    if (filterCategory === 'hospital') return s.id === 'pmjay' || s.id === 'arogya_karnataka';
    if (filterCategory === 'medicine') return s.id === 'pmbjp';
    if (filterCategory === 'screening') return s.id === 'ayushman_arogya_mandir';
    return true;
  });

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-200 gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 rounded-full bg-emerald-100 px-3 py-0.5 text-xs font-bold text-emerald-800 border border-emerald-200 mb-2">
            <Landmark className="h-3.5 w-3.5 text-emerald-700" />
            <span>National &amp; State Healthcare Assistance Portal</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900">
            Government Health Schemes &amp; Affordable Medicines
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Explore free ₹5 Lakh hospitalization coverage, 50–90% subsidized generic medicines, and free chronic disease screening.
          </p>
        </div>

        {/* Language Tabs */}
        <div className="flex items-center space-x-1.5 rounded-2xl bg-slate-100 p-1.5 border border-slate-200 self-start md:self-auto">
          <button
            type="button"
            onClick={() => setSelectedLang('en')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
              selectedLang === 'en'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            English
          </button>
          <button
            type="button"
            onClick={() => setSelectedLang('hi')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
              selectedLang === 'hi'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            हिंदी (Hindi)
          </button>
          <button
            type="button"
            onClick={() => setSelectedLang('kn')}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
              selectedLang === 'kn'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            ಕನ್ನಡ (Kannada)
          </button>
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center space-x-2 py-4 overflow-x-auto text-xs font-semibold">
        <button
          onClick={() => setFilterCategory('all')}
          className={`px-3.5 py-1.5 rounded-full border transition-all ${
            filterCategory === 'all'
              ? 'bg-slate-900 text-white border-slate-900'
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
          }`}
        >
          All Programs
        </button>
        <button
          onClick={() => setFilterCategory('hospital')}
          className={`px-3.5 py-1.5 rounded-full border transition-all ${
            filterCategory === 'hospital'
              ? 'bg-brand-600 text-white border-brand-600'
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
          }`}
        >
          ₹5 Lakh Hospitalization Cover
        </button>
        <button
          onClick={() => setFilterCategory('medicine')}
          className={`px-3.5 py-1.5 rounded-full border transition-all ${
            filterCategory === 'medicine'
              ? 'bg-purple-600 text-white border-purple-600'
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
          }`}
        >
          Generic Medicines (PMBJP)
        </button>
        <button
          onClick={() => setFilterCategory('screening')}
          className={`px-3.5 py-1.5 rounded-full border transition-all ${
            filterCategory === 'screening'
              ? 'bg-emerald-600 text-white border-emerald-600'
              : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
          }`}
        >
          Free Health Screening
        </button>
      </div>

      {/* Main Grid: List on left, Detail on right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pt-2">
        {/* Scheme List Cards */}
        <div className="lg:col-span-1 space-y-3">
          {loading ? (
            <div className="p-8 text-center text-xs text-slate-400">Loading verified schemes...</div>
          ) : (
            filtered.map((scheme) => {
              const isSelected = selectedScheme?.id === scheme.id;
              return (
                <div
                  key={scheme.id}
                  onClick={() => setSelectedScheme(scheme)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all text-left ${
                    isSelected
                      ? 'border-emerald-500 bg-emerald-50/50 shadow-xs ring-2 ring-emerald-500/20'
                      : 'border-slate-200 bg-slate-50/60 hover:bg-slate-100 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-start justify-between mb-1.5">
                    <span className="text-xs font-bold text-slate-900">{scheme.name}</span>
                    <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
                      {scheme.coverage_amount}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 line-clamp-2 leading-relaxed mb-2">
                    {scheme.summary}
                  </p>
                  <div className="flex items-center justify-between pt-1 border-t border-slate-200/60 text-[10px]">
                    <span className="text-slate-500 font-medium">Helpline: {scheme.helpline.split('/')[0]}</span>
                    <a
                      href={scheme.official_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      className="text-brand-600 hover:text-brand-800 font-bold inline-flex items-center space-x-0.5"
                    >
                      <span>Open Portal</span>
                      <ExternalLink className="h-2.5 w-2.5" />
                    </a>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Selected Scheme Deep-Dive Card */}
        <div className="lg:col-span-2 rounded-2xl border border-slate-200 bg-slate-50/70 p-6">
          {selectedScheme ? (
            <div className="space-y-5">
              <div>
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <h3 className="text-lg font-black text-slate-900">{selectedScheme.full_name}</h3>
                  <span className="rounded-full bg-emerald-600 px-3 py-1 text-xs font-bold text-white shadow-xs">
                    {selectedScheme.coverage_amount}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed font-normal">
                  {selectedScheme.summary}
                </p>
              </div>

              {/* Key Benefits */}
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-2">
                  Key Coverage &amp; Benefits:
                </span>
                <div className="space-y-1.5">
                  {selectedScheme.key_benefits.map((b, i) => (
                    <div key={i} className="flex items-start space-x-2 text-xs text-slate-800">
                      <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{b}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Eligibility & How to apply */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
                <div className="rounded-xl border border-slate-200 bg-white p-3.5">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                    Who is Eligible?
                  </span>
                  <p className="text-xs text-slate-700 leading-relaxed font-medium">
                    {selectedScheme.eligibility}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-3.5">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                    How to Apply / Avail:
                  </span>
                  <p className="text-xs text-slate-700 leading-relaxed font-medium">
                    {selectedScheme.how_to_apply}
                  </p>
                </div>
              </div>

              {/* Footer Actions with Direct Working Links */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-200">
                <div className="flex items-center space-x-2 text-xs font-bold text-slate-800">
                  <Phone className="h-4 w-4 text-brand-600" />
                  <span>Helpline: {selectedScheme.helpline}</span>
                </div>

                <div className="flex items-center space-x-2">
                  <a
                    href={selectedScheme.official_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1.5 rounded-xl bg-slate-900 px-4 py-2 text-xs font-bold text-white hover:bg-slate-800 transition-colors shadow-xs"
                  >
                    <span>Visit Official Government Portal</span>
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-slate-400">Select a scheme to view details.</div>
          )}
        </div>
      </div>
    </div>
  );
};
