export interface User {
  user_id: string;
  email: string;
  full_name: string;
  created_at?: string;
}

export interface AuthState {
  token: string | null;
  user: User | null;
}

export interface LifestyleFactors {
  age: number;
  sex: string;
  bmi: number;
  smoking_status: string;
  physical_activity_hours_per_week: number;
  mediterranean_diet_score: number;
  systolic_bp: number;
  sleep_hours: number;
  alcohol_drinks_per_week: number;
  family_history_cad: boolean;
  family_history_t2d: boolean;
  family_history_ad: boolean;
}

export interface DiseaseRiskResult {
  disease_id: string;
  disease_name: string;
  prs_raw_score: number;
  prs_standardized_z: number;
  prs_percentile: number;
  snps_found: number;
  snps_total: number;
  confidence_score: number;
  fused_relative_risk: number;
  fused_absolute_risk_10yr: number;
  risk_category: 'Low' | 'Average' | 'Elevated' | 'High';
  genetic_contribution_pct: number;
  lifestyle_contribution_pct: number;
  shap_mode: 'real_shap' | 'approximate_linear';
  shap_feature_importance: Record<string, number>;
  shap_waterfall_plot_b64?: string;
  key_risk_drivers: string[];
}

export interface ClinVarAnnotation {
  rsid: string;
  gene: string;
  clinical_significance: string;
  review_status: string;
  phenotype: string;
  accession: string;
}

export interface PharmGKBAnnotation {
  rsid: string;
  gene: string;
  drug: string;
  phenotype_category: string;
  clinical_recommendation: string;
  level_of_evidence: string;
}

export interface EvidenceCitation {
  title: string;
  citation: string;
  video_url?: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  timestamp: string;
  patient_summary: Record<string, any>;
  disease_risks: DiseaseRiskResult[];
  clinvar_pathogenic_findings: ClinVarAnnotation[];
  pharmgkb_alerts: PharmGKBAnnotation[];
  ai_explanation_narrative: string;
  ai_lifestyle_prescriptions: string[];
  evidence_citations: EvidenceCitation[];
  pdf_report_base64?: string;
  system_status: Record<string, any>;
}

export interface SimulationResponse {
  disease_id: string;
  simulated_relative_risk: number;
  simulated_absolute_risk_10yr: number;
  risk_delta_pct: number;
  simulated_category: string;
  actionable_levers: Array<{
    lever: string;
    potential_reduction_pct: number;
    impact: string;
  }>;
}

export interface DemoSample {
  id: string;
  title: string;
  tag?: string;
  description: string;
  lifestyle: LifestyleFactors;
  genomic_data: Record<string, number>;
}

export interface HistoryItem {
  history_id: string;
  user_id: string;
  timestamp: string;
  analysis_id: string;
  patient_summary: Record<string, any>;
  disease_risks: DiseaseRiskResult[];
  clinvar_pathogenic_findings: ClinVarAnnotation[];
  pharmgkb_alerts: PharmGKBAnnotation[];
  ai_explanation_narrative: string;
  ai_lifestyle_prescriptions: string[];
  pdf_report_base64?: string;
}

export interface GovtScheme {
  id: string;
  name: string;
  full_name: string;
  category: string;
  coverage_amount: string;
  summary: string;
  key_benefits: string[];
  eligibility: string;
  how_to_apply: string;
  helpline: string;
  official_url: string;
}

export interface AgentChatMessage {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  intent?: string;
  citations?: EvidenceCitation[];
  suggestedActions?: string[];
  timestamp: string;
}
