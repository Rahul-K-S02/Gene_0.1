'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  LifestyleFactors,
  AnalysisResponse,
  DemoSample,
  DiseaseRiskResult,
  User,
} from '../lib/types';
import {
  checkBackendHealth,
  fetchDemoSamples,
  analyzeRiskDirect,
  saveAnalysisToHistory,
  refreshToken,
  logoutUser,
} from '../lib/api';

import { Navbar } from '../components/Navbar';
import { DemoPresetSelector } from '../components/DemoPresetSelector';
import { FileUploadZone } from '../components/FileUploadZone';
import { LifestyleForm } from '../components/LifestyleForm';
import { RiskOverviewCard } from '../components/RiskOverviewCard';
import { BellCurveChart } from '../components/BellCurveChart';
import { WhatIfSimulator } from '../components/WhatIfSimulator';
import { ShapWaterfall } from '../components/ShapWaterfall';
import { PharmGKBCard } from '../components/PharmGKBCard';
import { RagExplanation } from '../components/RagExplanation';
import { RagChatModal } from '../components/RagChatModal';
import { GenomicsHandbookModal } from '../components/GenomicsHandbookModal';
import { CommonDiseasesAwareness } from '../components/CommonDiseasesAwareness';
import { GovtSchemesSection } from '../components/GovtSchemesSection';
import { AuthModal } from '../components/AuthModal';
import { HistoryDashboard } from '../components/HistoryDashboard';
import { MedicalAiChatbot } from '../components/MedicalAiChatbot';

import { Sparkles, FileCheck, Landmark, BookOpen, AlertCircle, ShieldCheck, HeartPulse, Ribbon } from 'lucide-react';

const DEFAULT_LIFESTYLE: LifestyleFactors = {
  age: 48,
  sex: 'male',
  bmi: 27.4,
  smoking_status: 'former',
  physical_activity_hours_per_week: 2.0,
  mediterranean_diet_score: 6,
  systolic_bp: 128,
  diastolic_bp: 82,
  sleep_hours: 7.0,
  alcohol_drinks_per_week: 3.0,
  family_history_cad: true,
  family_history_t2d: false,
  family_history_ad: false,
};

export default function HomePage() {
  const [systemOnline, setSystemOnline] = useState(true);
  const [demoSamples, setDemoSamples] = useState<DemoSample[]>([]);
  const [selectedDemoId, setSelectedDemoId] = useState<string | null>(null);

  const [user, setUser] = useState<User | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  const [lifestyle, setLifestyle] = useState<LifestyleFactors>(DEFAULT_LIFESTYLE);
  const [genomicData, setGenomicData] = useState<Record<string, number>>({});
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);

  const [language, setLanguage] = useState<string>('en');
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [selectedDiseaseId, setSelectedDiseaseId] = useState<string>('cad');

  // Modals state
  const [isHandbookOpen, setIsHandbookOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isChatModalOpen, setIsChatModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const schemesSectionRef = useRef<HTMLDivElement>(null);

  // Initial load
  useEffect(() => {
    async function init() {
      const health = await checkBackendHealth();
      setSystemOnline(health.status === 'online');

      try {
        const samples = await fetchDemoSamples();
        setDemoSamples(samples);
      } catch (e) {
        console.warn('Could not load remote demo samples:', e);
      }

      // Check URL query parameters for Google OAuth redirect callback
      if (typeof window !== 'undefined') {
        const urlParams = new URLSearchParams(window.location.search);
        const urlToken = urlParams.get('token');
        const urlEmail = urlParams.get('email');
        const urlUserId = urlParams.get('user_id');
        const urlFullName = urlParams.get('full_name');

        if (urlToken && urlEmail) {
          const newUser: User = {
            user_id: urlUserId || `usr_google_${absHash(urlEmail)}`,
            email: urlEmail,
            full_name: urlFullName || 'Google User',
          };
          handleAuthSuccess(urlToken, newUser);
          window.history.replaceState({}, document.title, window.location.pathname);
          return;
        }
      }

      // Restore session from stored token — call /auth/refresh to validate
      // This is what real-world apps (Gmail, GitHub) do: silently restore session on boot
      const savedToken = localStorage.getItem('generisk_auth_token');
      if (savedToken) {
        try {
          const refreshed = await refreshToken(savedToken);
          // Token is valid — restore and extend it
          const restoredUser: User = {
            user_id: refreshed.user_id,
            email: refreshed.email,
            full_name: refreshed.full_name,
          };
          handleAuthSuccess(refreshed.token, restoredUser);
        } catch {
          // Token expired or invalid — clear it, user must sign in again
          localStorage.removeItem('generisk_auth_token');
          localStorage.removeItem('generisk_user');
        }
      }
    }
    init();
  }, []);

  function absHash(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash) % 1000000;
  }

  const handleAuthSuccess = (token: string, userData: User) => {
    setAuthToken(token);
    setUser(userData);
    localStorage.setItem('generisk_auth_token', token);
    localStorage.setItem('generisk_user', JSON.stringify(userData));
  };

  const handleLogout = async () => {
    if (authToken) await logoutUser(authToken);
    setAuthToken(null);
    setUser(null);
    localStorage.removeItem('generisk_auth_token');
    localStorage.removeItem('generisk_user');
  };

  const handleSelectDemo = (sample: DemoSample) => {
    setSelectedDemoId(sample.id);
    setLifestyle(sample.lifestyle);
    setGenomicData(sample.genomic_data);
    setSelectedFileName(`Preloaded Profile: ${sample.title}`);
    setErrorMessage(null);
  };

  const handleGenomicDataReady = (data: Record<string, number>, fileName: string) => {
    setGenomicData(data);
    setSelectedFileName(fileName);
    setSelectedDemoId(null);
    setErrorMessage(null);
  };

  const handleClearFile = () => {
    setSelectedFileName(null);
    setGenomicData({});
    setSelectedDemoId(null);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setErrorMessage(null);

    try {
      const result = await analyzeRiskDirect(lifestyle, genomicData, language);
      setAnalysisResult(result);
      if (result.disease_risks.length > 0) {
        setSelectedDiseaseId(result.disease_risks[0].disease_id);
      }

      // Automatically save to MongoDB history if authenticated
      if (authToken) {
        saveAnalysisToHistory(result, authToken);
      }

      // Smooth scroll to results
      setTimeout(() => {
        const resultsEl = document.getElementById('results-dashboard');
        if (resultsEl) {
          resultsEl.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    } catch (err: any) {
      setErrorMessage(err?.message || 'Analysis failed. Please check inputs.');
    } finally {
      setLoading(false);
    }
  };

  const scrollToSchemes = () => {
    schemesSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const selectedDiseaseObj: DiseaseRiskResult | undefined =
    analysisResult?.disease_risks.find((d) => d.disease_id === selectedDiseaseId) ||
    analysisResult?.disease_risks[0];

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      {/* Top Navbar */}
      <Navbar
        onOpenHandbook={() => setIsHandbookOpen(true)}
        onOpenSchemes={scrollToSchemes}
        onOpenHistory={() => setIsHistoryOpen(true)}
        onOpenAuth={() => setIsAuthOpen(true)}
        user={user}
        onLogout={handleLogout}
        language={language}
        onLanguageChange={setLanguage}
        systemOnline={systemOnline}
      />

      {/* Hero Header */}
      <div className="bg-gradient-to-b from-brand-50/70 via-slate-50 to-slate-50 border-b border-slate-200/80 py-10 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-5xl text-center">
          <div className="inline-flex items-center space-x-2 rounded-full bg-brand-100 px-3.5 py-1 text-xs font-bold text-brand-800 border border-brand-200 mb-4 shadow-2xs">
            <Sparkles className="h-3.5 w-3.5 text-brand-600" />
            <span>Automated In-Browser VCF Streaming &bull; Explainable SHAP &bull; Ayushman Schemes</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-slate-900 leading-tight">
            AI-Powered Genomic Risk Intelligence
          </h1>
          <p className="mt-3 text-sm sm:text-base text-slate-600 max-w-2xl mx-auto leading-relaxed font-normal">
            Understand your inherited disease susceptibility, discover how daily lifestyle counteracts genetic risk, and access government healthcare benefits.
          </p>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="mx-auto max-w-7xl flex-1 px-4 sm:px-6 lg:px-8 py-8 w-full space-y-8">
        {/* Error Alert */}
        {errorMessage && (
          <div className="flex items-center space-x-3 rounded-2xl border border-rose-300 bg-rose-50 p-4 text-rose-900 shadow-sm">
            <AlertCircle className="h-5 w-5 text-rose-600 shrink-0" />
            <div className="text-xs font-medium">
              <p className="font-bold mb-0.5">Analysis Failed</p>
              <p>{errorMessage}</p>
            </div>
          </div>
        )}

        {/* 1-Click Everyday Patient Profiles */}
        {demoSamples.length > 0 && (
          <DemoPresetSelector
            samples={demoSamples}
            selectedId={selectedDemoId}
            onSelectSample={handleSelectDemo}
          />
        )}

        {/* Genomic Upload & Questionnaire Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* File Upload Zone */}
          <div className="lg:col-span-1">
            <FileUploadZone
              onGenomicDataReady={handleGenomicDataReady}
              selectedFileName={selectedFileName}
              onClearFile={handleClearFile}
            />
          </div>

          {/* Lifestyle Questionnaire */}
          <div className="lg:col-span-2">
            <LifestyleForm
              lifestyle={lifestyle}
              onChange={setLifestyle}
              onSubmit={handleAnalyze}
              loading={loading}
            />
          </div>
        </div>

        {/* Results Dashboard */}
        {analysisResult && selectedDiseaseObj && (
          <div id="results-dashboard" className="space-y-8 pt-6 border-t border-slate-200">
            {/* Results Title Banner */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-6 sm:p-8 text-white shadow-xl gap-4">
              <div>
                <div className="flex items-center space-x-2.5 mb-1">
                  <FileCheck className="h-5 w-5 text-brand-400" />
                  <h2 className="text-lg sm:text-xl font-bold">
                    Clinical Genomic Assessment: {analysisResult.analysis_id}
                  </h2>
                </div>
                <p className="text-xs text-slate-300 font-normal">
                  Evaluated on {new Date(analysisResult.timestamp).toLocaleString()} | Synced with MongoDB Atlas &bull; Ephemeral Zero-Disk Mode
                </p>
              </div>

              <div className="flex items-center space-x-3">
                <button
                  type="button"
                  onClick={() => setIsChatModalOpen(true)}
                  className="rounded-2xl bg-brand-600 px-5 py-2.5 text-xs font-bold text-white hover:bg-brand-500 transition-all shadow-md shadow-brand-500/30"
                >
                  Ask AI About Report
                </button>
              </div>
            </div>

            {/* Multi-Disease Overview */}
            <RiskOverviewCard
              diseaseRisks={analysisResult.disease_risks}
              selectedDiseaseId={selectedDiseaseId}
              onSelectDisease={setSelectedDiseaseId}
            />

            {/* Selected Disease Deep-Dive Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Population Bell Curve */}
              <BellCurveChart
                diseaseName={selectedDiseaseObj.disease_name}
                userPercentile={selectedDiseaseObj.prs_percentile}
                userZScore={selectedDiseaseObj.prs_standardized_z}
              />

              {/* SHAP Waterfall Feature Importance */}
              <ShapWaterfall disease={selectedDiseaseObj} />
            </div>

            {/* Interactive What-If Simulator */}
            <WhatIfSimulator
              disease={selectedDiseaseObj}
              initialLifestyle={lifestyle}
            />

            {/* Pharmacogenomics & ClinVar Alerts */}
            <PharmGKBCard
              pharmgkbAlerts={analysisResult.pharmgkb_alerts}
              clinvarFindings={analysisResult.clinvar_pathogenic_findings}
            />

            {/* RAG Clinical Narrative & Citations */}
            <RagExplanation
              narrative={analysisResult.ai_explanation_narrative}
              prescriptions={analysisResult.ai_lifestyle_prescriptions}
              citations={analysisResult.evidence_citations}
              pdfBase64={analysisResult.pdf_report_base64}
              onOpenChat={() => setIsChatModalOpen(true)}
            />
          </div>
        )}

        {/* Common Diseases & Cancer Awareness Hub */}
        <div className="pt-2">
          <CommonDiseasesAwareness />
        </div>

        {/* Government Healthcare Schemes & Affordable Medicine Portal */}
        <div ref={schemesSectionRef} className="pt-4">
          <GovtSchemesSection currentLang={language} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-8 text-center text-xs text-slate-500">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <span>&copy; {new Date().getFullYear()} GeneRisk 2.0 &bull; AI-Powered Genomic Risk Intelligence &amp; Public Health Portal.</span>
          <span className="text-[11px] text-slate-400 font-medium">
            Standardized Genetics (P+T) &bull; SHAP Explainability &bull; MongoDB Atlas &bull; Ayushman Bharat Portal
          </span>
        </div>
      </footer>

      {/* Modals & Floating Widgets */}
      <GenomicsHandbookModal
        isOpen={isHandbookOpen}
        onClose={() => setIsHandbookOpen(false)}
      />

      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      <HistoryDashboard
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        token={authToken}
        onSelectReport={(report) => {
          setAnalysisResult(report);
          if (report.disease_risks.length > 0) {
            setSelectedDiseaseId(report.disease_risks[0].disease_id);
          }
          setTimeout(() => {
            document.getElementById('results-dashboard')?.scrollIntoView({ behavior: 'smooth' });
          }, 100);
        }}
      />

      <RagChatModal
        isOpen={isChatModalOpen}
        onClose={() => setIsChatModalOpen(false)}
        reportSummary={analysisResult ? analysisResult.patient_summary : {}}
        language={language}
      />

      {/* 24/7 Medical AI Agent Chatbot */}
      <MedicalAiChatbot
        patientContext={analysisResult ? analysisResult.patient_summary : undefined}
        language={language}
      />
    </div>
  );
}
