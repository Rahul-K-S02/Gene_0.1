'use client';

import React, { useState } from 'react';
import { LifestyleFactors } from '../lib/types';
import { UserCheck, Heart, Scale, Cigarette, Dumbbell, Utensils, Moon, Wine, Activity, Calculator, Info } from 'lucide-react';

interface LifestyleFormProps {
  lifestyle: LifestyleFactors;
  onChange: (lifestyle: LifestyleFactors) => void;
  onSubmit: () => void;
  loading: boolean;
}

export const LifestyleForm: React.FC<LifestyleFormProps> = ({
  lifestyle,
  onChange,
  onSubmit,
  loading,
}) => {
  const [heightCm, setHeightCm] = useState(175);
  const [weightKg, setWeightKg] = useState(78);
  const [showBmiCalc, setShowBmiCalc] = useState(false);
  const [showBpHelper, setShowBpHelper] = useState(false);

  const updateField = <K extends keyof LifestyleFactors>(
    field: K,
    value: LifestyleFactors[K]
  ) => {
    onChange({ ...lifestyle, [field]: value });
  };

  const handleHeightWeightChange = (h: number, w: number) => {
    setHeightCm(h);
    setWeightKg(w);
    if (h > 50 && w > 20) {
      const calculatedBmi = Number((w / Math.pow(h / 100, 2)).toFixed(1));
      updateField('bmi', calculatedBmi);
    }
  };

  const getBmiCategory = (bmi: number) => {
    if (bmi < 18.5) return { label: 'Underweight', color: 'text-blue-600 bg-blue-50 border-blue-200' };
    if (bmi < 25.0) return { label: 'Normal / Healthy', color: 'text-emerald-600 bg-emerald-50 border-emerald-200' };
    if (bmi < 30.0) return { label: 'Overweight', color: 'text-amber-600 bg-amber-50 border-amber-200' };
    return { label: 'Obese (Class I+)', color: 'text-rose-600 bg-rose-50 border-rose-200' };
  };

  const bmiCat = getBmiCategory(lifestyle.bmi);

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
        <div className="flex items-center space-x-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-brand-100 text-brand-600">
            <UserCheck className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-base font-black text-slate-900">
              Personal &amp; Lifestyle Questionnaire
            </h3>
            <p className="text-xs text-slate-500">Factors that turn genetic risk up or down</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5">
        {/* Age */}
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1">Age (Years)</label>
          <input
            type="number"
            min={18}
            max={100}
            value={lifestyle.age}
            onChange={(e) => updateField('age', parseInt(e.target.value) || 45)}
            className="w-full rounded-2xl border border-slate-300 px-3.5 py-2.5 text-xs font-semibold focus:border-brand-500 focus:ring-1 focus:ring-brand-500 bg-white"
          />
        </div>

        {/* Sex */}
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1">Biological Sex</label>
          <select
            value={lifestyle.sex}
            onChange={(e) => updateField('sex', e.target.value)}
            className="w-full rounded-2xl border border-slate-300 px-3.5 py-2.5 text-xs font-semibold focus:border-brand-500 bg-white cursor-pointer"
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other / Prefer not to say</option>
          </select>
        </div>

        {/* BMI with Calculator Helper */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-bold text-slate-700">Body Mass Index (BMI)</label>
            <button
              type="button"
              onClick={() => setShowBmiCalc(!showBmiCalc)}
              className="flex items-center space-x-1 text-[11px] font-bold text-brand-600 hover:underline"
            >
              <Calculator className="h-3 w-3" />
              <span>{showBmiCalc ? 'Enter direct' : 'Calc from Height/Weight'}</span>
            </button>
          </div>

          {showBmiCalc ? (
            <div className="space-y-2 rounded-2xl bg-slate-50 p-3 border border-slate-200">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <span className="text-[10px] text-slate-500 font-bold block mb-0.5">Height (cm)</span>
                  <input
                    type="number"
                    value={heightCm}
                    onChange={(e) =>
                      handleHeightWeightChange(parseFloat(e.target.value) || 170, weightKg)
                    }
                    className="w-full rounded-xl border border-slate-300 px-2.5 py-1.5 text-xs bg-white font-semibold"
                  />
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 font-bold block mb-0.5">Weight (kg)</span>
                  <input
                    type="number"
                    value={weightKg}
                    onChange={(e) =>
                      handleHeightWeightChange(heightCm, parseFloat(e.target.value) || 70)
                    }
                    className="w-full rounded-xl border border-slate-300 px-2.5 py-1.5 text-xs bg-white font-semibold"
                  />
                </div>
              </div>
              <div className="flex items-center justify-between text-[11px] pt-1">
                <span className="font-bold text-slate-700">BMI: {lifestyle.bmi} kg/m²</span>
                <span className={`px-2 py-0.5 rounded-full border text-[10px] font-bold ${bmiCat.color}`}>
                  {bmiCat.label}
                </span>
              </div>
            </div>
          ) : (
            <div>
              <div className="relative">
                <input
                  type="number"
                  step="0.1"
                  min={12}
                  max={60}
                  value={lifestyle.bmi}
                  onChange={(e) => updateField('bmi', parseFloat(e.target.value) || 25.0)}
                  className="w-full rounded-2xl border border-slate-300 px-3.5 py-2.5 text-xs font-semibold focus:border-brand-500 bg-white"
                />
                <span className="absolute right-3.5 top-2.5 text-xs text-slate-400 font-semibold">
                  kg/m²
                </span>
              </div>
              <div className="mt-1 flex items-center justify-between">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${bmiCat.color}`}>
                  {bmiCat.label}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Systolic Blood Pressure with Category Helper */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="text-xs font-bold text-slate-700">Systolic Blood Pressure (BP)</label>
            <button
              type="button"
              onClick={() => setShowBpHelper(!showBpHelper)}
              className="text-[11px] font-bold text-brand-600 hover:underline"
            >
              {showBpHelper ? 'Enter number' : 'Don\'t know BP?'}
            </button>
          </div>

          {showBpHelper ? (
            <div className="rounded-2xl bg-slate-50 p-2.5 border border-slate-200 space-y-1 text-[11px]">
              <button
                type="button"
                onClick={() => {
                  updateField('systolic_bp', 118);
                  setShowBpHelper(false);
                }}
                className="w-full text-left p-1.5 rounded-lg hover:bg-white font-medium text-slate-700"
              >
                💚 Normal / Healthy (~118 mmHg)
              </button>
              <button
                type="button"
                onClick={() => {
                  updateField('systolic_bp', 128);
                  setShowBpHelper(false);
                }}
                className="w-full text-left p-1.5 rounded-lg hover:bg-white font-medium text-slate-700"
              >
                💛 Slightly Elevated (~128 mmHg)
              </button>
              <button
                type="button"
                onClick={() => {
                  updateField('systolic_bp', 138);
                  setShowBpHelper(false);
                }}
                className="w-full text-left p-1.5 rounded-lg hover:bg-white font-medium text-slate-700"
              >
                🧡 Stage 1 High BP (~138 mmHg)
              </button>
              <button
                type="button"
                onClick={() => {
                  updateField('systolic_bp', 148);
                  setShowBpHelper(false);
                }}
                className="w-full text-left p-1.5 rounded-lg hover:bg-white font-medium text-slate-700"
              >
                ❤️ Stage 2 High BP / On Pills (~148 mmHg)
              </button>
            </div>
          ) : (
            <div className="relative">
              <input
                type="number"
                min={80}
                max={240}
                value={lifestyle.systolic_bp}
                onChange={(e) => updateField('systolic_bp', parseInt(e.target.value) || 120)}
                className="w-full rounded-2xl border border-slate-300 px-3.5 py-2.5 text-xs font-semibold focus:border-brand-500 bg-white"
              />
              <span className="absolute right-3.5 top-2.5 text-xs text-slate-400 font-semibold">
                mmHg
              </span>
            </div>
          )}
        </div>

        {/* Smoking */}
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1">Smoking Habit</label>
          <select
            value={lifestyle.smoking_status}
            onChange={(e) => updateField('smoking_status', e.target.value)}
            className="w-full rounded-2xl border border-slate-300 px-3.5 py-2.5 text-xs font-semibold focus:border-brand-500 bg-white cursor-pointer"
          >
            <option value="never">Never Smoked</option>
            <option value="former">Former Smoker (Quit)</option>
            <option value="current">Current Smoker</option>
          </select>
        </div>

        {/* Physical Activity */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="text-xs font-bold text-slate-700">Weekly Exercise</label>
            <span className="text-xs font-black text-brand-600">
              {lifestyle.physical_activity_hours_per_week} hrs/wk
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="12"
            step="0.5"
            value={lifestyle.physical_activity_hours_per_week}
            onChange={(e) =>
              updateField('physical_activity_hours_per_week', parseFloat(e.target.value))
            }
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
          />
        </div>

        {/* Mediterranean Diet */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="text-xs font-bold text-slate-700">Healthy Diet Score</label>
            <span className="text-xs font-black text-brand-600">
              {lifestyle.mediterranean_diet_score} / 10
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="10"
            step="1"
            value={lifestyle.mediterranean_diet_score}
            onChange={(e) =>
              updateField('mediterranean_diet_score', parseInt(e.target.value))
            }
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
          />
        </div>

        {/* Sleep Duration */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="text-xs font-bold text-slate-700">Sleep Duration</label>
            <span className="text-xs font-black text-brand-600">
              {lifestyle.sleep_hours} hrs/night
            </span>
          </div>
          <input
            type="range"
            min="4"
            max="12"
            step="0.5"
            value={lifestyle.sleep_hours}
            onChange={(e) => updateField('sleep_hours', parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
          />
        </div>

        {/* Alcohol */}
        <div>
          <label className="block text-xs font-bold text-slate-700 mb-1">
            Alcohol Drinks / Week
          </label>
          <input
            type="number"
            min={0}
            max={50}
            value={lifestyle.alcohol_drinks_per_week}
            onChange={(e) =>
              updateField('alcohol_drinks_per_week', parseFloat(e.target.value) || 0)
            }
            className="w-full rounded-2xl border border-slate-300 px-3.5 py-2.5 text-xs font-semibold focus:border-brand-500 bg-white"
          />
        </div>
      </div>

      {/* Family History */}
      <div className="mt-6 border-t border-slate-100 pt-5">
        <span className="block text-xs font-black uppercase tracking-wider text-slate-700 mb-3">
          Family Medical History (Parents or Siblings)
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <label className="flex items-center space-x-3 rounded-2xl border border-slate-200 p-3.5 text-xs font-semibold text-slate-800 cursor-pointer hover:bg-slate-50 transition-colors">
            <input
              type="checkbox"
              checked={lifestyle.family_history_cad}
              onChange={(e) => updateField('family_history_cad', e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
            />
            <span>Heart Disease / Heart Attack</span>
          </label>

          <label className="flex items-center space-x-3 rounded-2xl border border-slate-200 p-3.5 text-xs font-semibold text-slate-800 cursor-pointer hover:bg-slate-50 transition-colors">
            <input
              type="checkbox"
              checked={lifestyle.family_history_t2d}
              onChange={(e) => updateField('family_history_t2d', e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
            />
            <span>Type 2 Diabetes</span>
          </label>

          <label className="flex items-center space-x-3 rounded-2xl border border-slate-200 p-3.5 text-xs font-semibold text-slate-800 cursor-pointer hover:bg-slate-50 transition-colors">
            <input
              type="checkbox"
              checked={lifestyle.family_history_ad}
              onChange={(e) => updateField('family_history_ad', e.target.checked)}
              className="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
            />
            <span>Alzheimer&apos;s Dementia</span>
          </label>
        </div>
      </div>

      {/* CTA Button */}
      <div className="mt-7 flex justify-end">
        <button
          type="button"
          onClick={onSubmit}
          disabled={loading}
          className="flex items-center space-x-2.5 rounded-2xl bg-gradient-to-r from-brand-600 to-indigo-600 px-7 py-3.5 text-xs sm:text-sm font-black text-white shadow-md shadow-brand-500/25 hover:from-brand-700 hover:to-indigo-700 transition-all disabled:opacity-50"
        >
          {loading ? (
            <>
              <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Analyzing Genetic PRS &amp; SHAP...</span>
            </>
          ) : (
            <>
              <Activity className="h-4 w-4" />
              <span>Generate Full Genomic Risk Report</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};
