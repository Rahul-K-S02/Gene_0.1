'use client';

import React, { useState } from 'react';
import {
  BookOpen, X, Dna, Sparkles, HeartPulse, ShieldCheck,
  Pill, CheckCircle2, ChevronRight, Activity, Play, ExternalLink,
  Sliders, Flame, Award, Lightbulb
} from 'lucide-react';

interface GenomicsHandbookModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GenomicsHandbookModal: React.FC<GenomicsHandbookModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'dna' | 'vcf' | 'risk' | 'epigenetics' | 'pgx' | 'videos'>('dna');
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);

  if (!isOpen) return null;

  const VIDEO_LIST = [
    {
      id: 'zwibgNGe46Y',
      title: 'What is DNA and How Does it Work?',
      channel: 'Stated Clearly',
      duration: '5:24',
      category: 'DNA Basics',
      summary: 'Crystal-clear animation on how DNA code builds living organisms and proteins.'
    },
    {
      id: 'tJjXpiWKMyA',
      title: 'Single Nucleotide Polymorphisms (SNPs) Explained',
      channel: 'DNA Learning Center',
      duration: '4:15',
      category: 'Genetic Variants',
      summary: 'Learn how single letter variations (A, T, C, G) make us unique and alter health risks.'
    },
    {
      id: 'k50yMwEOWGU',
      title: 'Epigenetics: How Lifestyle Changes Genetic Expression',
      channel: 'TED-Ed',
      duration: '5:03',
      category: 'Epigenetics',
      summary: 'Discover how nutrition, exercise, and sleep turn disease-causing genes ON or OFF.'
    },
    {
      id: '0k57_6f5y28',
      title: 'Pharmacogenomics: Why Medicines Work Differently',
      channel: 'Mayo Clinic',
      duration: '3:45',
      category: 'Medication Safety',
      summary: 'How liver enzyme genetics protect you from adverse drug reactions and statin toxicity.'
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-3 sm:p-4">
      <div className="flex flex-col h-[720px] w-full max-w-3xl rounded-3xl bg-white shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-200 bg-gradient-to-r from-brand-600 via-indigo-600 to-purple-700 px-6 py-4 text-white">
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 text-white backdrop-blur-xs shadow-inner">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold">DNA &amp; Genomics Patient Handbook</h3>
                <span className="rounded-full bg-white/20 px-2 py-0.5 text-[10px] font-bold text-brand-100">
                  Interactive Guide + Videos
                </span>
              </div>
              <p className="text-xs text-brand-100">Visual guide to understanding your genetic risk, DNA, VCF files &amp; lifestyle power</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-xl p-2 text-white/80 hover:bg-white/10 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 bg-slate-50 px-3 overflow-x-auto text-xs font-bold scrollbar-none">
          <button
            onClick={() => setActiveTab('dna')}
            className={`py-3 px-3.5 border-b-2 whitespace-nowrap transition-all ${
              activeTab === 'dna'
                ? 'border-brand-600 text-brand-700 bg-white shadow-2xs'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            1. DNA &amp; Genes
          </button>
          <button
            onClick={() => setActiveTab('vcf')}
            className={`py-3 px-3.5 border-b-2 whitespace-nowrap transition-all ${
              activeTab === 'vcf'
                ? 'border-brand-600 text-brand-700 bg-white shadow-2xs'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            2. What is a VCF?
          </button>
          <button
            onClick={() => setActiveTab('risk')}
            className={`py-3 px-3.5 border-b-2 whitespace-nowrap transition-all ${
              activeTab === 'risk'
                ? 'border-brand-600 text-brand-700 bg-white shadow-2xs'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            3. Polygenic Risk (PRS)
          </button>
          <button
            onClick={() => setActiveTab('epigenetics')}
            className={`py-3 px-3.5 border-b-2 whitespace-nowrap transition-all ${
              activeTab === 'epigenetics'
                ? 'border-brand-600 text-brand-700 bg-white shadow-2xs'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            4. Epigenetics Power
          </button>
          <button
            onClick={() => setActiveTab('pgx')}
            className={`py-3 px-3.5 border-b-2 whitespace-nowrap transition-all ${
              activeTab === 'pgx'
                ? 'border-brand-600 text-brand-700 bg-white shadow-2xs'
                : 'border-transparent text-slate-500 hover:text-slate-900'
            }`}
          >
            5. Drug Safety (PGx)
          </button>
          <button
            onClick={() => setActiveTab('videos')}
            className={`py-3 px-3.5 border-b-2 whitespace-nowrap transition-all flex items-center space-x-1 ${
              activeTab === 'videos'
                ? 'border-rose-600 text-rose-700 bg-white shadow-2xs'
                : 'border-transparent text-rose-600 hover:text-rose-900'
            }`}
          >
            <Play className="h-3 w-3 fill-current" />
            <span>Video Explanations</span>
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5 text-slate-700 text-xs sm:text-sm leading-relaxed">
          
          {/* TAB 1: DNA & GENES */}
          {activeTab === 'dna' && (
            <div className="space-y-4">
              <div className="flex items-center space-x-4 rounded-2xl bg-gradient-to-r from-brand-50 to-indigo-50 p-4 border border-brand-200">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-600 text-white shadow-md shrink-0">
                  <Dna className="h-6 w-6 animate-pulse" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-900 text-base">Your Biological Instruction Manual</h4>
                  <p className="text-xs text-slate-600 mt-0.5">
                    Inside every one of your 37 trillion cells lies DNA — a sequence of 3 billion letters (<strong>A, T, C, G</strong>) inherited from your biological parents.
                  </p>
                </div>
              </div>

              {/* Animated DNA Sequence Diagram */}
              <div className="rounded-2xl border border-slate-200 bg-slate-900 p-4 text-white">
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-2 font-mono">
                  <span>Chromosome 9 (9p21.3 Locus)</span>
                  <span className="text-emerald-400">Live Base-Pair Animation</span>
                </div>
                <div className="flex justify-between items-center py-2 px-3 bg-slate-800/80 rounded-xl font-mono text-sm tracking-widest overflow-x-auto">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded border border-blue-500/30">A</span>
                    <span className="text-slate-500">─</span>
                    <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded border border-emerald-500/30">T</span>
                    <span className="text-slate-500">─</span>
                    <span className="px-2 py-1 bg-amber-500/20 text-amber-400 rounded border border-amber-500/30 animate-pulse font-black">C (Risk)</span>
                    <span className="text-slate-500">─</span>
                    <span className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded border border-purple-500/30">G</span>
                    <span className="text-slate-500">─</span>
                    <span className="px-2 py-1 bg-rose-500/20 text-rose-400 rounded border border-rose-500/30">A</span>
                  </div>
                  <span className="text-xs font-bold text-amber-400 pl-4">SNP: rs1333049</span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-1">
                <div className="rounded-2xl border border-slate-200 p-4 bg-slate-50">
                  <h5 className="font-bold text-slate-900 flex items-center space-x-1.5 mb-1.5">
                    <span className="text-base">🧬</span>
                    <span>What is a Gene?</span>
                  </h5>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    A gene is a specific sentence in your DNA that tells your body how to build proteins, process dietary fats, or produce insulin. Humans have approximately 20,000 genes.
                  </p>
                </div>
                <div className="rounded-2xl border border-slate-200 p-4 bg-slate-50">
                  <h5 className="font-bold text-slate-900 flex items-center space-x-1.5 mb-1.5">
                    <span className="text-base">🔍</span>
                    <span>What is a SNP Variant?</span>
                  </h5>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    99.9% of human DNA is identical. The remaining 0.1% consists of single letter variations (SNPs) like <i>rs1333049</i> that influence hair color, height, and disease risk.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: VCF FILE */}
          {activeTab === 'vcf' && (
            <div className="space-y-4">
              <div className="rounded-2xl bg-indigo-50 p-4 border border-indigo-200">
                <h4 className="font-bold text-indigo-950 text-base mb-1">What is a VCF (Variant Call Format) File?</h4>
                <p className="text-xs text-indigo-800 leading-relaxed">
                  When a laboratory sequences your DNA, printing all 3 billion letters would create a file the size of 500 phone books. Instead, they generate a <strong>VCF file</strong> that records <em>only where your letters differ from the reference human genome</em>.
                </p>
              </div>

              {/* Visual Breakdown of VCF line */}
              <div className="rounded-2xl bg-slate-900 p-4 font-mono text-[11px] text-slate-300 space-y-2 border border-slate-800">
                <div className="flex items-center justify-between text-slate-400 border-b border-slate-800 pb-2">
                  <span className="font-bold text-emerald-400"># Interactive VCF Line Dissection:</span>
                  <span className="text-[10px] text-slate-500">GRCh38 Coordinates</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80 space-y-1">
                  <div className="flex flex-wrap gap-2 text-xs font-bold">
                    <span className="text-emerald-400">chr9</span>
                    <span className="text-blue-400">22125503</span>
                    <span className="text-amber-400">rs1333049</span>
                    <span className="text-purple-400">C</span>
                    <span className="text-purple-300">G</span>
                    <span className="text-slate-400">PASS</span>
                    <span className="text-rose-400">GT: 0/1</span>
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 text-[10px] text-slate-400 border-t border-slate-800/50">
                    <div><span className="text-emerald-400 font-bold">chr9</span>: Chromosome</div>
                    <div><span className="text-blue-400 font-bold">22125503</span>: Exact Base Locus</div>
                    <div><span className="text-amber-400 font-bold">rs1333049</span>: NCBI Database ID</div>
                    <div><span className="text-rose-400 font-bold">0/1</span>: 1 Risk Copy Inherited</div>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 p-4 bg-slate-50">
                <h5 className="font-bold text-slate-900 mb-1 flex items-center space-x-2">
                  <Sparkles className="h-4 w-4 text-brand-600" />
                  <span>Automated In-Browser Streaming in GeneRisk</span>
                </h5>
                <p className="text-xs text-slate-600 leading-relaxed">
                  You do not need to download Python scripts or split files manually. GeneRisk streams your VCF file in chunks inside your web browser, extracts the lead GWAS risk alleles in 2 seconds, and never saves raw files to disk.
                </p>
              </div>
            </div>
          )}

          {/* TAB 3: POLYGENIC RISK */}
          {activeTab === 'risk' && (
            <div className="space-y-4">
              <div className="rounded-2xl bg-rose-50 p-4 border border-rose-200">
                <h4 className="font-bold text-rose-950 text-base mb-1">How Polygenic Risk Scores (PRS) Work</h4>
                <p className="text-xs text-rose-800 leading-relaxed">
                  Common conditions like Heart Attack or Type 2 Diabetes are rarely caused by one broken gene. Instead, they are <strong>Polygenic</strong> — driven by the combined sum of dozens of small genetic nudges.
                </p>
              </div>

              {/* Bell Curve Infographic */}
              <div className="rounded-2xl border border-slate-200 bg-gradient-to-b from-slate-50 to-white p-4">
                <h5 className="font-bold text-slate-900 text-xs mb-2">Population Normal Distribution of Genetic Risk:</h5>
                <div className="h-16 flex items-end justify-between px-4 border-b-2 border-slate-300 pb-1 relative">
                  <div className="w-1/5 h-4 bg-emerald-200 rounded-t text-center text-[9px] font-bold text-emerald-800 pt-0.5">Low (0-20%)</div>
                  <div className="w-3/5 h-14 bg-blue-200 rounded-t text-center text-[9px] font-bold text-blue-800 pt-2">Average Population Bell Curve (20-80%)</div>
                  <div className="w-1/5 h-8 bg-rose-300 rounded-t text-center text-[9px] font-bold text-rose-900 pt-1 relative">
                    High (80-100%)
                    <span className="absolute -top-5 right-2 text-[9px] font-black text-rose-600 animate-bounce">▲ You are here</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 mt-2">
                  A 90th percentile PRS means your genetic background places you in the top 10% of inherited susceptibility compared to the general population.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                <div className="rounded-xl border border-slate-200 p-3 bg-slate-50 flex items-start space-x-2.5">
                  <HeartPulse className="h-5 w-5 text-rose-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-slate-900 text-xs block">Heart Disease (CAD - 9p21.3)</span>
                    <span className="text-[11px] text-slate-600">Variants in ANRIL/CDKN2B make artery walls attract LDL cholesterol faster under high blood pressure.</span>
                  </div>
                </div>
                <div className="rounded-xl border border-slate-200 p-3 bg-slate-50 flex items-start space-x-2.5">
                  <Activity className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-slate-900 text-xs block">Type 2 Diabetes (TCF7L2)</span>
                    <span className="text-[11px] text-slate-600">Variants reduce pancreatic GLP-1 hormone release, making early insulin response slower after meals.</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: EPIGENETICS */}
          {activeTab === 'epigenetics' && (
            <div className="space-y-4">
              <div className="rounded-2xl bg-emerald-50 p-4 border border-emerald-200">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="h-5 w-5 text-emerald-700" />
                  <h4 className="font-bold text-emerald-950 text-base">The Power of Epigenetics: Genes are NOT Destiny!</h4>
                </div>
                <p className="text-xs text-emerald-800 mt-1 leading-relaxed">
                  Your DNA sequence is fixed at birth, but your <strong>epigenome</strong> (the chemical tags that turn genes ON or OFF) changes every day based on your lifestyle choices.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="rounded-2xl border border-emerald-200 bg-white p-4 text-center shadow-xs">
                  <div className="flex h-10 w-10 mx-auto items-center justify-center rounded-full bg-emerald-100 text-emerald-700 mb-2">
                    <Flame className="h-5 w-5" />
                  </div>
                  <span className="text-xl font-black text-emerald-600 block">-48% Heart Risk</span>
                  <span className="text-xs font-bold text-slate-800 block mt-0.5">Cardioprotective Diet</span>
                  <span className="text-[11px] text-slate-500 leading-tight block mt-1">
                    Mediterranean fats &amp; high fiber suppress arterial inflammatory genes.
                  </span>
                </div>

                <div className="rounded-2xl border border-emerald-200 bg-white p-4 text-center shadow-xs">
                  <div className="flex h-10 w-10 mx-auto items-center justify-center rounded-full bg-blue-100 text-blue-700 mb-2">
                    <Activity className="h-5 w-5" />
                  </div>
                  <span className="text-xl font-black text-blue-600 block">-58% Diabetes Risk</span>
                  <span className="text-xs font-bold text-slate-800 block mt-0.5">150 Min/Wk Exercise</span>
                  <span className="text-[11px] text-slate-500 leading-tight block mt-1">
                    Aerobic movement forces muscle GLUT4 receptors to absorb glucose without insulin.
                  </span>
                </div>

                <div className="rounded-2xl border border-emerald-200 bg-white p-4 text-center shadow-xs">
                  <div className="flex h-10 w-10 mx-auto items-center justify-center rounded-full bg-purple-100 text-purple-700 mb-2">
                    <Award className="h-5 w-5" />
                  </div>
                  <span className="text-xl font-black text-purple-600 block">-35% Stroke Risk</span>
                  <span className="text-xs font-bold text-slate-800 block mt-0.5">Blood Pressure &lt;120</span>
                  <span className="text-[11px] text-slate-500 leading-tight block mt-1">
                    Reduces shearing stress on brain capillaries and halts aneurysm formation.
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: PHARMACOGENOMICS */}
          {activeTab === 'pgx' && (
            <div className="space-y-4">
              <div className="rounded-2xl bg-purple-50 p-4 border border-purple-200">
                <div className="flex items-center space-x-2">
                  <Pill className="h-5 w-5 text-purple-700" />
                  <h4 className="font-bold text-purple-950 text-base">Pharmacogenomics: Personalized Medicine Safety</h4>
                </div>
                <p className="text-xs text-purple-800 mt-1 leading-relaxed">
                  Your liver uses specific enzymes to activate or clear medications. Genetic variations determine whether standard doses are therapeutic, ineffective, or toxic.
                </p>
              </div>

              <div className="space-y-2.5">
                <div className="rounded-xl border border-slate-200 p-3.5 bg-slate-50">
                  <span className="font-bold text-slate-900 text-xs block mb-1">
                    💊 Simvastatin &amp; Muscle Pain (SLCO1B1 *5 Variant)
                  </span>
                  <p className="text-[11px] text-slate-600 leading-relaxed">
                    Carriers of the <i>rs4149056</i> variant have impaired liver uptake of Simvastatin, causing it to build up in muscle tissue and cause severe myopathy. Doctors switch carriers to Rosuvastatin or Pravastatin.
                  </p>
                </div>

                <div className="rounded-xl border border-slate-200 p-3.5 bg-slate-50">
                  <span className="font-bold text-slate-900 text-xs block mb-1">
                    🩸 Clopidogrel Resistance (CYP2C19 *2 Loss-of-Function)
                  </span>
                  <p className="text-[11px] text-slate-600 leading-relaxed">
                    Clopidogrel (Plavix) is a prodrug that must be activated by CYP2C19. Poor metabolizers cannot activate it effectively after stent placement, requiring Prasugrel or Ticagrelor.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: VIDEO EXPLANATIONS */}
          {activeTab === 'videos' && (
            <div className="space-y-4">
              <div className="rounded-2xl bg-rose-50 p-4 border border-rose-200">
                <div className="flex items-center space-x-2">
                  <Play className="h-5 w-5 text-rose-600 fill-current" />
                  <h4 className="font-bold text-rose-950 text-base">Curated Visual &amp; Video Explanations</h4>
                </div>
                <p className="text-xs text-rose-800 mt-1">
                  Watch top medical animations from reputable genetics institutes to understand your DNA report visually.
                </p>
              </div>

              {selectedVideo ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => setSelectedVideo(null)}
                      className="text-xs font-bold text-rose-600 hover:underline flex items-center space-x-1"
                    >
                      <span>← Back to Video List</span>
                    </button>
                    <a
                      href={`https://www.youtube.com/watch?v=${selectedVideo}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-1 text-xs font-bold text-slate-800 hover:text-rose-600 bg-slate-100 hover:bg-slate-200 px-3 py-1 rounded-xl transition-colors"
                    >
                      <span>Open on YouTube</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>

                  <div className="relative aspect-video w-full rounded-2xl overflow-hidden shadow-lg border border-slate-200 bg-black">
                    <iframe
                      src={`https://www.youtube-nocookie.com/embed/${selectedVideo}?autoplay=1&rel=0`}
                      title="Genomics Educational Video"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      className="w-full h-full"
                    />
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {VIDEO_LIST.map((video) => (
                    <div
                      key={video.id}
                      className="group rounded-2xl border border-slate-200 p-4 bg-white hover:border-rose-400 hover:shadow-md transition-all flex flex-col justify-between"
                    >
                      <div onClick={() => setSelectedVideo(video.id)} className="cursor-pointer">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-100">
                            {video.category}
                          </span>
                          <span className="text-[10px] text-slate-400 font-mono">{video.duration}</span>
                        </div>
                        <h5 className="font-bold text-slate-900 text-xs group-hover:text-rose-600 transition-colors">
                          {video.title}
                        </h5>
                        <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                          {video.summary}
                        </p>
                      </div>
                      
                      <div className="mt-3 flex items-center justify-between text-xs font-bold text-rose-600 border-t border-slate-100 pt-2">
                        <span className="text-[10px] text-slate-400 font-medium">{video.channel}</span>
                        <div className="flex items-center space-x-2">
                          <a
                            href={`https://www.youtube.com/watch?v=${video.id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-[10px] text-slate-500 hover:text-slate-800 underline flex items-center space-x-0.5"
                          >
                            <span>YouTube</span>
                            <ExternalLink className="h-2.5 w-2.5" />
                          </a>
                          <button
                            type="button"
                            onClick={() => setSelectedVideo(video.id)}
                            className="flex items-center space-x-1 bg-rose-50 hover:bg-rose-100 text-rose-700 px-2 py-0.5 rounded-md"
                          >
                            <span>Watch</span>
                            <Play className="h-2.5 w-2.5 fill-current" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 px-6 py-3.5">
          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <Lightbulb className="h-4 w-4 text-amber-500" />
            <span>GeneRisk Patient Empowerment Education Initiative</span>
          </div>
          <button
            onClick={onClose}
            className="rounded-xl bg-slate-900 px-4 py-2 text-xs font-bold text-white hover:bg-slate-800 transition-colors"
          >
            Close Handbook
          </button>
        </div>

      </div>
    </div>
  );
};
