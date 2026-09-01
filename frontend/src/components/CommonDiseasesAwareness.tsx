'use client';

import React, { useState } from 'react';
import {
  ShieldAlert, HeartPulse, Activity, AlertTriangle, CheckCircle2,
  Calendar, Flame, Sparkles, Video, Play, ExternalLink, Info,
  Search, Stethoscope, ChevronRight, Ribbon, Pill, Landmark
} from 'lucide-react';

interface DiseaseCategory {
  id: string;
  name: string;
  badge: string;
  color: string;
  icon: any;
  overview: string;
  redFlags: string[];
  screeningSchedule: { test: string; ageGroup: string; frequency: string }[];
  geneticFactors: string;
  precautions: string[];
  govtSchemeCoverage: string;
  govtPortalUrl: string;
  youtubeId: string;
  videoTitle: string;
  videoChannel: string;
}

export const CommonDiseasesAwareness: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState<string>('cancer');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [playingVideoId, setPlayingVideoId] = useState<string | null>(null);

  const CATEGORIES: DiseaseCategory[] = [
    {
      id: 'cancer',
      name: 'Cancer Early Detection & Prevention',
      badge: 'High Awareness',
      color: 'rose',
      icon: Ribbon,
      overview: 'Cancer is caused by abnormal cellular proliferation driven by DNA mutations in tumor suppressors (TP53, BRCA1/2). Early detection before metastasis increases 5-year survival rates above 90%.',
      redFlags: [
        'Unexplained persistent weight loss (>5 kg in 1-2 months)',
        'Hard, painless lump in breast, neck, testicle, or lymph node',
        'Unusual bleeding (abnormal vaginal bleeding, coughing blood, dark stool)',
        'Non-healing sore inside the mouth, tongue, or on skin (>3 weeks)',
        'Persistent hoarseness of voice or difficulty swallowing',
        'Obvious changes in size, color, or borders of a mole (ABCD rule)'
      ],
      screeningSchedule: [
        { test: 'Mammography (Breast)', ageGroup: 'Women 40-74 yrs', frequency: 'Every 1-2 years' },
        { test: 'Colonoscopy (Colon/Rectum)', ageGroup: 'Adults 45-75 yrs', frequency: 'Every 10 years (or annual FIT)' },
        { test: 'Pap Smear / HPV DNA (Cervical)', ageGroup: 'Women 21-65 yrs', frequency: 'Pap every 3 yrs / HPV every 5 yrs' },
        { test: 'Low-Dose CT (Lung)', ageGroup: 'Smokers 50-80 yrs (20 pack-yrs)', frequency: 'Annual scan' },
        { test: 'Oral Visual Exam', ageGroup: 'Tobacco / Gutkha users', frequency: 'Every 6-12 months' }
      ],
      geneticFactors: '10-15% of cancers are hereditary (BRCA1/BRCA2 in Breast/Ovarian, MLH1/MSH2 in Lynch Colorectal, TP53 in Li-Fraumeni).',
      precautions: [
        'Complete avoidance of all tobacco, beedi, cigarettes, and gutkha products.',
        'Receive prophylactic HPV Vaccination between ages 9 and 26.',
        'Consume 30g+ dietary fiber daily from whole grains, cruciferous vegetables, and antioxidant berries.',
        'Limit processed meats and maintain physical activity to prevent hormonal insulin surges.'
      ],
      govtSchemeCoverage: '100% Cashless oncology surgeries, radiation therapy, and chemotherapy regimens covered up to ₹5,00,000 under Ayushman Bharat PM-JAY.',
      govtPortalUrl: 'https://beneficiary.nha.gov.in',
      youtubeId: 'z4L3wu5D2eM',
      videoTitle: 'How Cancer Cells Grow & How Early Detection Saves Lives',
      videoChannel: 'TED-Ed / Oncology Guidelines'
    },
    {
      id: 'cad',
      name: 'Cardiovascular & Heart Attack',
      badge: 'Leading Cause of Mortality',
      color: 'red',
      icon: HeartPulse,
      overview: 'Coronary artery disease develops as atherosclerotic plaques narrow coronary vessels, causing angina and sudden myocardial infarction (heart attack).',
      redFlags: [
        'Acute squeezing pressure or heavy tightness in center of chest',
        'Pain radiating to left arm, neck, jaw, back, or upper stomach',
        'Sudden cold sweats, dizziness, extreme weakness, or nausea',
        'Unexplained shortness of breath on mild exertion or while lying flat'
      ],
      screeningSchedule: [
        { test: 'Lipid Profile (LDL, HDL, Triglycerides)', ageGroup: 'All adults 20+ yrs', frequency: 'Every 3-5 years (Annual if high risk)' },
        { test: 'Blood Pressure Measurement', ageGroup: 'All adults 18+ yrs', frequency: 'Every 6-12 months' },
        { test: 'Coronary Calcium Scan / TMT', ageGroup: 'Adults 40+ with family CAD', frequency: 'As advised by cardiologist' }
      ],
      geneticFactors: 'Heritability is 40-50%. Loci at 9p21.3 (rs1333049), APOB (rs693), LPA (rs10455872), and PCSK9 alter LDL clearance and plaque inflammation.',
      precautions: [
        'Maintain strict blood pressure below 120/80 mmHg.',
        'Follow an AHA Mediterranean diet high in omega-3 fatty acids, olive oil, and low in trans fats.',
        'Achieve at least 150 minutes of moderate aerobic exercise weekly.',
        'Keep LDL cholesterol <70 mg/dL (or <55 mg/dL if high risk).'
      ],
      govtSchemeCoverage: 'Coronary angioplasty, stent placement, and bypass surgeries (CABG) are covered cashlessly under PM-JAY and Arogya Karnataka.',
      govtPortalUrl: 'https://beneficiary.nha.gov.in',
      youtubeId: '3_PYnWVoUzM',
      videoTitle: 'How a Heart Attack Happens & How to Prevent It',
      videoChannel: 'TED-Ed / Dr. Sahil Parikh (AHA)'
    },
    {
      id: 'diabetes',
      name: 'Type 2 Diabetes & Metabolic Health',
      badge: 'Reversible in Early Stages',
      color: 'amber',
      icon: Activity,
      overview: 'Characterized by insulin resistance in skeletal muscle and liver combined with progressive pancreatic beta-cell dysfunction, leading to chronic microvascular damage.',
      redFlags: [
        'Excessive frequent urination, especially at night (polyuria)',
        'Constant excessive thirst and dry mouth (polydipsia)',
        'Unexplained weight loss despite increased hunger',
        'Tingling, burning sensation, or numbness in feet and toes (neuropathy)',
        'Slow-healing foot wounds, cuts, or frequent fungal infections',
        'Blurry vision and sudden visual fluctuations'
      ],
      screeningSchedule: [
        { test: 'Fasting Blood Glucose & HbA1c', ageGroup: 'Adults 35+ yrs (or BMI >25)', frequency: 'Every 1-3 years' },
        { test: 'Urine Albumin-to-Creatinine Ratio', ageGroup: 'Diagnosed Diabetics', frequency: 'Annual kidney check' },
        { test: 'Dilated Eye Exam (Retinopathy)', ageGroup: 'Diagnosed Diabetics', frequency: 'Annual eye check' }
      ],
      geneticFactors: 'Strong polygenic susceptibility mediated by TCF7L2 (rs7903146), KCNJ11 (rs5215), and PPARG (rs1801282).',
      precautions: [
        'Target a 5-10% body weight reduction in overweight/obese individuals.',
        'Adopt a low-glycemic index diet; avoid sugar-sweetened beverages and refined white flour.',
        'Combine aerobic fitness with resistance training to boost insulin receptor sensitivity.',
        'Target HbA1c below 6.5% for prediabetes reversal.'
      ],
      govtSchemeCoverage: 'Generic Metformin, Glimepiride, and Teneligliptin are available at 70-90% discount at PM Jan Aushadhi Kendras. Free screenings at Ayushman Arogya Mandirs.',
      govtPortalUrl: 'https://janaushadhi.gov.in',
      youtubeId: 'MGL6km115JA',
      videoTitle: 'How Does Diabetes Work & How Can You Reverse It?',
      videoChannel: 'TED-Ed / ADA Standards of Care'
    },
    {
      id: 'stroke',
      name: 'Hypertension & Acute Stroke',
      badge: 'Time-Critical Emergency',
      color: 'purple',
      icon: AlertTriangle,
      overview: 'High blood pressure causes microvascular damage and arterial rupture or clot formation, depriving brain tissue of oxygen (1.9 million neurons lost per minute).',
      redFlags: [
        'B.E. F.A.S.T. Warning Checklist:',
        '• Balance: Sudden loss of balance, dizziness, or coordination',
        '• Eyes: Sudden loss of vision or double vision in one or both eyes',
        '• Face: One side of face droops when smiling',
        '• Arm: One arm drifts downward when raised',
        '• Speech: Slurred speech or inability to repeat a simple sentence',
        '• Time: Call 108 / 112 immediately — 4.5 hour golden window for tPA thrombolysis!'
      ],
      screeningSchedule: [
        { test: 'Home BP Monitoring', ageGroup: 'Adults with SBP >120', frequency: 'Twice weekly' },
        { test: 'Carotid Doppler Ultrasound', ageGroup: 'High risk / TIA patients', frequency: 'As clinically indicated' },
        { test: 'Electrocardiogram (ECG) for Atrial Fibrillation', ageGroup: 'Adults 50+ yrs', frequency: 'Annual physical' }
      ],
      geneticFactors: 'Variants in renin-angiotensin (AGT, ACE) and nitric oxide synthase (NOS3) genes regulate vascular tone and endothelial health.',
      precautions: [
        'Limit dietary sodium to <2,000 mg/day (less than 1 teaspoon of table salt).',
        'Adopt the DASH diet (high in potassium, magnesium, and calcium from leafy greens and nuts).',
        'Eliminate binge alcohol consumption to prevent acute blood pressure spikes.',
        'Practice daily stress reduction and diaphragmatic breathing.'
      ],
      govtSchemeCoverage: 'Acute stroke stabilization and ICU care are covered under emergency protocols of Ayushman Bharat and Karnataka Harish Scheme.',
      govtPortalUrl: 'https://beneficiary.nha.gov.in',
      youtubeId: 'pcmhA_53K6E',
      videoTitle: 'What Happens During a Stroke & B.E. F.A.S.T. Signs',
      videoChannel: 'TED-Ed / Dr. Vaibhav Goswami (AHA / ASA)'
    }
  ];

  const filteredCategories = CATEGORIES.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.overview.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.redFlags.some(f => f.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const currentCategory = CATEGORIES.find(c => c.id === activeCategory) || CATEGORIES[0];

  return (
    <section id="disease-awareness" className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-rose-50 text-rose-600">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <h2 className="text-xl font-black tracking-tight text-slate-900">
              Common Diseases &amp; Cancer Awareness Hub
            </h2>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Evidence-based precautions, screening schedules, and early warning signs for life-threatening conditions.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search disease or symptom..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-xl border border-slate-200 bg-slate-50 pl-9 pr-3 py-2 text-xs font-medium text-slate-800 placeholder-slate-400 focus:bg-white focus:border-brand-500 focus:outline-hidden"
          />
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex flex-wrap gap-2 pt-6">
        {filteredCategories.map((cat) => {
          const IconComp = cat.icon;
          const isActive = cat.id === activeCategory;
          return (
            <button
              key={cat.id}
              onClick={() => {
                setActiveCategory(cat.id);
                setPlayingVideoId(null);
              }}
              className={`flex items-center space-x-2 rounded-2xl px-4 py-2.5 text-xs font-bold transition-all ${
                isActive
                  ? 'bg-slate-900 text-white shadow-md'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              <IconComp className={`h-4 w-4 ${isActive ? 'text-rose-400' : 'text-slate-500'}`} />
              <span>{cat.name}</span>
            </button>
          );
        })}
      </div>

      {/* Main Content Pane */}
      <div className="mt-6 space-y-6">
        {/* Overview Box */}
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
            <h3 className="text-base font-black text-slate-900 flex items-center space-x-2">
              <span>{currentCategory.name}</span>
            </h3>
            <span className="rounded-full bg-rose-100 text-rose-800 px-2.5 py-0.5 text-[10px] font-bold">
              {currentCategory.badge}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
            {currentCategory.overview}
          </p>
        </div>

        {/* 2-Column Grid: Warning Signs & Screening Schedule */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Red Flag Warning Signs */}
          <div className="rounded-2xl border border-rose-200 bg-rose-50/40 p-5 space-y-3">
            <div className="flex items-center space-x-2 text-rose-700">
              <AlertTriangle className="h-5 w-5 shrink-0" />
              <h4 className="text-xs sm:text-sm font-black uppercase tracking-wider">
                Red-Flag Warning Signs (Seek Medical Review)
              </h4>
            </div>
            <ul className="space-y-2">
              {currentCategory.redFlags.map((flag, idx) => (
                <li key={idx} className="flex items-start space-x-2 text-xs text-slate-800 font-medium">
                  <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-rose-200 text-rose-800 text-[10px] font-black mt-0.5">
                    !
                  </span>
                  <span>{flag}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recommended Screening Timetable */}
          <div className="rounded-2xl border border-blue-200 bg-blue-50/40 p-5 space-y-3">
            <div className="flex items-center space-x-2 text-blue-700">
              <Calendar className="h-5 w-5 shrink-0" />
              <h4 className="text-xs sm:text-sm font-black uppercase tracking-wider">
                Standard Clinical Screening Schedules
              </h4>
            </div>
            <div className="space-y-2">
              {currentCategory.screeningSchedule.map((s, idx) => (
                <div key={idx} className="rounded-xl border border-blue-100 bg-white p-3 space-y-1">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-900">
                    <span>{s.test}</span>
                    <span className="text-[10px] font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md">
                      {s.frequency}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 font-medium">
                    Target Group: {s.ageGroup}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Prevention Precautions & Genetic Context */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Precautions */}
          <div className="lg:col-span-2 rounded-2xl border border-emerald-200 bg-emerald-50/40 p-5 space-y-3">
            <div className="flex items-center space-x-2 text-emerald-800">
              <CheckCircle2 className="h-5 w-5 shrink-0" />
              <h4 className="text-xs sm:text-sm font-black uppercase tracking-wider">
                Evidence-Based Prevention Precautions
              </h4>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {currentCategory.precautions.map((p, idx) => (
                <div key={idx} className="rounded-xl border border-emerald-100 bg-white p-3 text-xs text-slate-800 flex items-start space-x-2 shadow-2xs">
                  <span className="text-emerald-600 font-black">✓</span>
                  <span>{p}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Genetic Context & Financial Support */}
          <div className="rounded-2xl border border-purple-200 bg-purple-50/40 p-5 space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-1.5 text-purple-800 text-xs font-bold mb-1.5">
                <Sparkles className="h-4 w-4" />
                <span>Genetic Heritability Role</span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed">
                {currentCategory.geneticFactors}
              </p>
            </div>

            <div className="border-t border-purple-200/60 pt-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-bold text-purple-800 uppercase tracking-wider block">
                  Govt Scheme Coverage:
                </span>
                <a
                  href={currentCategory.govtPortalUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1 text-[10px] font-bold text-brand-600 hover:text-brand-800 hover:underline"
                >
                  <span>Check Portal</span>
                  <ExternalLink className="h-2.5 w-2.5" />
                </a>
              </div>
              <p className="text-[11px] text-purple-950 font-medium leading-relaxed bg-white/80 p-2.5 rounded-xl border border-purple-100">
                {currentCategory.govtSchemeCoverage}
              </p>
            </div>
          </div>
        </div>

        {/* Embedded Video Education Player with Direct YouTube Link Fallback */}
        <div className="rounded-2xl border border-slate-200 bg-slate-900 p-5 text-white">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
            <div className="flex items-center space-x-2">
              <Video className="h-5 w-5 text-rose-400 shrink-0" />
              <div>
                <h4 className="text-xs sm:text-sm font-bold">
                  Medical Video Guide: {currentCategory.videoTitle}
                </h4>
                <p className="text-[10px] text-slate-400">Source: {currentCategory.videoChannel}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <a
                href={`https://www.youtube.com/watch?v=${currentCategory.youtubeId}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 px-3 py-1.5 text-xs font-bold text-slate-200 transition-colors border border-slate-700"
              >
                <span>Open in YouTube</span>
                <ExternalLink className="h-3.5 w-3.5" />
              </a>

              {playingVideoId !== currentCategory.youtubeId && (
                <button
                  type="button"
                  onClick={() => setPlayingVideoId(currentCategory.youtubeId)}
                  className="inline-flex items-center space-x-1.5 rounded-xl bg-rose-600 hover:bg-rose-700 px-3 py-1.5 text-xs font-bold transition-colors shadow-xs"
                >
                  <Play className="h-3.5 w-3.5 fill-current" />
                  <span>Play Here</span>
                </button>
              )}
            </div>
          </div>

          {playingVideoId === currentCategory.youtubeId ? (
            <div className="space-y-2">
              <div className="relative aspect-video w-full rounded-xl overflow-hidden shadow-2xl border border-slate-800">
                <iframe
                  src={`https://www.youtube-nocookie.com/embed/${currentCategory.youtubeId}?autoplay=1&rel=0&modestbranding=1`}
                  title={currentCategory.videoTitle}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                  className="w-full h-full"
                />
              </div>
              <div className="flex justify-between items-center text-[11px] text-slate-400 pt-1">
                <span>If video playback is restricted by your browser, use the &quot;Open in YouTube&quot; button above.</span>
                <button
                  onClick={() => setPlayingVideoId(null)}
                  className="text-xs text-rose-400 hover:underline font-bold"
                >
                  Close Player
                </button>
              </div>
            </div>
          ) : (
            <div
              onClick={() => setPlayingVideoId(currentCategory.youtubeId)}
              className="group relative aspect-video sm:h-48 w-full rounded-xl bg-slate-800 border border-slate-700 flex flex-col items-center justify-center cursor-pointer hover:bg-slate-750 transition-all overflow-hidden"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-600 text-white shadow-xl group-hover:scale-110 transition-transform">
                <Play className="h-6 w-6 fill-current ml-0.5" />
              </div>
              <p className="text-xs font-bold text-slate-200 mt-2">
                Click to watch clinical breakdown
              </p>
              <span className="text-[10px] text-slate-400">Verified medical education source ({currentCategory.videoChannel})</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
