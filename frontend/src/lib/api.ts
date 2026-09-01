import {
  AnalysisResponse,
  SimulationResponse,
  DemoSample,
  LifestyleFactors,
  HistoryItem,
  GovtScheme,
  User,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// --- System Health ---
export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: 'no-store' });
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (error) {
    return { status: 'offline', error: String(error) };
  }
}

// --- Auth Services ---
export async function registerUser(email: string, password: string, fullName: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Registration failed');
  }
  return res.json();
}

export async function loginUser(email: string, password: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Login failed');
  }
  return res.json();
}

export async function loginWithGoogle(idToken: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/google`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_token: idToken }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Google sign-in failed');
  }
  return res.json();
}

export async function refreshToken(token: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('Token expired or invalid');
  return res.json(); // { token, user_id, email, full_name }
}

export async function logoutUser(token: string) {
  await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => {}); // best-effort
}

// --- History Services ---
export async function saveAnalysisToHistory(analysis: AnalysisResponse, token?: string) {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE_URL}/api/v1/history/save`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      analysis_id: analysis.analysis_id,
      patient_summary: analysis.patient_summary,
      disease_risks: analysis.disease_risks,
      clinvar_pathogenic_findings: analysis.clinvar_pathogenic_findings,
      pharmgkb_alerts: analysis.pharmgkb_alerts,
      ai_explanation_narrative: analysis.ai_explanation_narrative,
      ai_lifestyle_prescriptions: analysis.ai_lifestyle_prescriptions,
      pdf_report_base64: analysis.pdf_report_base64,
    }),
  });
  if (!res.ok) return null;
  return res.json();
}

export async function fetchUserHistory(token: string): Promise<HistoryItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/history`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: 'no-store',
  });
  if (!res.ok) throw new Error('Failed to load history');
  return res.json();
}

export async function deleteHistoryItem(historyId: string, token: string) {
  const res = await fetch(`${API_BASE_URL}/api/v1/history/${historyId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.ok;
}

// --- Government Schemes ---
export async function fetchGovtSchemes(lang: string = 'en'): Promise<GovtScheme[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/govt-schemes?lang=${lang}`, {
    cache: 'no-store',
  });
  if (!res.ok) throw new Error('Failed to fetch schemes');
  return res.json();
}

// --- Medical AI Health Assistant Chatbot ---
export async function sendAgentChatMessage(
  message: string,
  history: Array<{ role: string; content: string }> = [],
  patientContext?: Record<string, any>,
  language: string = 'en'
) {
  const res = await fetch(`${API_BASE_URL}/api/v1/agent-chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      conversation_history: history,
      patient_context: patientContext,
      language,
    }),
  });
  if (!res.ok) throw new Error('Chat assistant response failed');
  return res.json();
}

// --- Legacy Report Chat ---
export async function sendChatQuestion(
  question: string,
  reportSummary: Record<string, any>,
  language: string = 'en'
) {
  const res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      report_summary: reportSummary,
      language,
    }),
  });
  if (!res.ok) throw new Error('Chat request failed');
  return res.json();
}

// --- Core Genomic Analysis ---
export async function fetchDemoSamples(): Promise<DemoSample[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/demo-samples`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to load demo samples');
  return res.json();
}

export async function analyzeRiskDirect(
  lifestyle: LifestyleFactors,
  genomicData: Record<string, number> = {},
  language: string = 'en'
): Promise<AnalysisResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      lifestyle,
      genomic_data: genomicData,
      language,
    }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Analysis failed: ${errorText}`);
  }

  return res.json();
}

export async function analyzeRiskWithVcf(
  file: File,
  lifestyle: LifestyleFactors,
  language: string = 'en'
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('lifestyle_json', JSON.stringify(lifestyle));
  formData.append('language', language);

  const res = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`VCF analysis failed: ${errorText}`);
  }

  return res.json();
}

export async function simulateLifestyle(
  diseaseId: string,
  basePrsPercentile: number,
  basePrsZ: number,
  lifestyle: LifestyleFactors
): Promise<SimulationResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      disease_id: diseaseId,
      base_prs_percentile: basePrsPercentile,
      base_prs_z: basePrsZ,
      lifestyle,
    }),
  });

  if (!res.ok) throw new Error('Simulation failed');
  return res.json();
}
