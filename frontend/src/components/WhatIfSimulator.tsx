'use client';

import React, { useState, useEffect } from 'react';
import { LifestyleFactors, SimulationResponse, DiseaseRiskResult } from '../lib/types';
import { simulateLifestyle } from '../lib/api';
import { Sliders, Sparkles, TrendingDown, TrendingUp, CheckCircle, ArrowRight } from 'lucide-react';

interface WhatIfSimulatorProps {
  disease: DiseaseRiskResult;
  initialLifestyle: LifestyleFactors;
}

export const WhatIfSimulator: React.FC<WhatIfSimulatorProps> = ({
  disease,
  initialLifestyle,
}) => {
  const [simLifestyle, setSimLifestyle] = useState<LifestyleFactors>({ ...initialLifestyle });
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setSimLifestyle({ ...initialLifestyle });
  }, [initialLifestyle]);

  useEffect(() => {
    let isCancelled = false;
    const runSimulation = async () => {
      setLoading(true);
      try {
        const res = await simulateLifestyle(
          disease.disease_id,
          disease.prs_percentile,
          disease.prs_standardized_z,
          simLifestyle
        );
        if (!isCancelled) {
          setSimulation(res);
        }
      } catch (err) {
        console.error('Simulation error:', err);
      } finally {
        if (!isCancelled) setLoading(false);
      }
    };

    const timer = setTimeout(runSimulation, 250);
    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [simLifestyle, disease]);

  const updateSim = <K extends keyof LifestyleFactors>(field: K, val: LifestyleFactors[K]) => {
    setSimLifestyle((prev) => ({ ...prev, [field]: val }));
  };

  const initialAR = disease.fused_absolute_risk_10yr * 100;
  const currentAR = simulation ? simulation.simulated_absolute_risk_10yr * 100 : initialAR;
  const deltaAR = currentAR - initialAR;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-5 gap-2">
        <div className="flex items-center space-x-2">
          <Sliders className="h-5 w-5 text-brand-600" />
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Interactive &quot;What-If&quot; Lifestyle Risk Simulator
            </h3>
            <p className="text-xs text-slate-500">
              Adjust modifiable factors live to see how lifestyle changes counter genetic susceptibility for{' '}
              <span className="font-semibold text-slate-700">{disease.disease_name}</span>.
            </p>
          </div>
        </div>

        {/* Live Delta Pill */}
        <div
          className={`flex items-center space-x-2 rounded-xl px-4 py-2 text-xs font-bold border transition-all self-start sm:self-auto ${
            deltaAR < -0.1
              ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
              : deltaAR > 0.1
              ? 'bg-rose-50 text-rose-800 border-rose-300'
              : 'bg-slate-100 text-slate-700 border-slate-300'
          }`}
        >
          {deltaAR < -0.1 ? (
            <TrendingDown className="h-4 w-4 text-emerald-600" />
          ) : deltaAR > 0.1 ? (
            <TrendingUp className="h-4 w-4 text-rose-600" />
          ) : null}
          <span>
            {deltaAR < -0.1
              ? `Absolute Risk Drops by ${Math.abs(deltaAR).toFixed(1)}%`
              : deltaAR > 0.1
              ? `Absolute Risk Increases by +${deltaAR.toFixed(1)}%`
              : 'Current Baseline Setting'}
          </span>
        </div>
      </div>

      {/* Comparison Scoreboard */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6 rounded-xl bg-slate-50 p-4 border border-slate-200">
        <div>
          <span className="text-[11px] uppercase font-bold text-slate-400 block">
            Baseline 10-Yr Absolute Risk
          </span>
          <span className="text-xl font-black text-slate-800">{initialAR.toFixed(1)}%</span>
          <span className="text-[11px] text-slate-500 block">Current profile</span>
        </div>

        <div className="sm:border-x sm:border-slate-200 sm:px-4">
          <span className="text-[11px] uppercase font-bold text-slate-400 block">
            Simulated 10-Yr Risk
          </span>
          <span
            className={`text-xl font-black ${
              deltaAR < -0.1
                ? 'text-emerald-600'
                : deltaAR > 0.1
                ? 'text-rose-600'
                : 'text-slate-800'
            }`}
          >
            {currentAR.toFixed(1)}%
          </span>
          <span className="text-[11px] text-slate-500 block">
            Category: {simulation?.simulated_category || disease.risk_category}
          </span>
        </div>

        <div>
          <span className="text-[11px] uppercase font-bold text-slate-400 block">
            Simulated Relative Risk
          </span>
          <span className="text-xl font-black text-slate-800">
            {simulation?.simulated_relative_risk.toFixed(2) || disease.fused_relative_risk.toFixed(2)}x
          </span>
          <span className="text-[11px] text-slate-500 block">vs average population</span>
        </div>
      </div>

      {/* Simulator Sliders */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* BMI Slider */}
        <div className="rounded-xl border border-slate-200 p-3.5 bg-white">
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-xs font-semibold text-slate-700">Simulate BMI</span>
            <span className="text-xs font-bold text-brand-600">{simLifestyle.bmi} kg/m²</span>
          </div>
          <input
            type="range"
            min="18.5"
            max="40.0"
            step="0.5"
            value={simLifestyle.bmi}
            onChange={(e) => updateSim('bmi', parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
          />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>Normal (18.5)</span>
            <span>Overweight (25)</span>
            <span>Obese (30+)</span>
          </div>
        </div>

        {/* Smoking Toggle */}
        <div className="rounded-xl border border-slate-200 p-3.5 bg-white">
          <span className="text-xs font-semibold text-slate-700 block mb-2">
            Simulate Smoking Status
          </span>
          <div className="grid grid-cols-3 gap-1.5">
            {(['never', 'former', 'current'] as const).map((status) => (
              <button
                key={status}
                type="button"
                onClick={() => updateSim('smoking_status', status)}
                className={`py-1.5 text-xs font-bold rounded-lg border capitalize transition-all ${
                  simLifestyle.smoking_status === status
                    ? 'bg-brand-600 text-white border-brand-600 shadow-xs'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        </div>

        {/* Exercise Slider */}
        <div className="rounded-xl border border-slate-200 p-3.5 bg-white">
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-xs font-semibold text-slate-700">Simulate Exercise</span>
            <span className="text-xs font-bold text-brand-600">
              {simLifestyle.physical_activity_hours_per_week} hrs/wk
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="12"
            step="0.5"
            value={simLifestyle.physical_activity_hours_per_week}
            onChange={(e) =>
              updateSim('physical_activity_hours_per_week', parseFloat(e.target.value))
            }
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
          />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>Sedentary (0)</span>
            <span>Target (2.5-5.0)</span>
            <span>Athletic (8+)</span>
          </div>
        </div>

        {/* Systolic BP */}
        <div className="rounded-xl border border-slate-200 p-3.5 bg-white">
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-xs font-semibold text-slate-700">Simulate Systolic BP</span>
            <span className="text-xs font-bold text-brand-600">{simLifestyle.systolic_bp} mmHg</span>
          </div>
          <input
            type="range"
            min="100"
            max="180"
            step="2"
            value={simLifestyle.systolic_bp}
            onChange={(e) => updateSim('systolic_bp', parseInt(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
          />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>Optimal (&lt;120)</span>
            <span>Stage 1 (130)</span>
            <span>Stage 2 (140+)</span>
          </div>
        </div>

        {/* Mediterranean Diet */}
        <div className="rounded-xl border border-slate-200 p-3.5 bg-white">
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-xs font-semibold text-slate-700">Simulate Diet Quality</span>
            <span className="text-xs font-bold text-brand-600">
              {simLifestyle.mediterranean_diet_score} / 10
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="10"
            step="1"
            value={simLifestyle.mediterranean_diet_score}
            onChange={(e) => updateSim('mediterranean_diet_score', parseInt(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
          />
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>Low (0-4)</span>
            <span>Moderate (5-7)</span>
            <span>High (8-10)</span>
          </div>
        </div>

        {/* Reset Button */}
        <div className="flex flex-col justify-center rounded-xl border border-dashed border-slate-300 p-3.5 bg-slate-50/50">
          <button
            type="button"
            onClick={() => setSimLifestyle({ ...initialLifestyle })}
            className="w-full rounded-lg bg-white border border-slate-300 py-2.5 text-xs font-bold text-slate-700 hover:bg-slate-100 transition-colors shadow-xs"
          >
            Reset to Real Patient Baseline
          </button>
        </div>
      </div>

      {/* Actionable Levers Identified */}
      {simulation && simulation.actionable_levers.length > 0 && (
        <div className="mt-5 border-t border-slate-100 pt-4">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-700 block mb-2.5">
            Highest-Yield Actionable Levers for this Condition
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {simulation.actionable_levers.map((lever, i) => (
              <div
                key={i}
                className="flex items-center justify-between rounded-xl bg-emerald-50/60 border border-emerald-200 p-3 text-xs"
              >
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-emerald-600 shrink-0" />
                  <span className="font-semibold text-emerald-950">{lever.lever}</span>
                </div>
                <span className="font-extrabold text-emerald-700 whitespace-nowrap ml-2">
                  -{lever.potential_reduction_pct}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
