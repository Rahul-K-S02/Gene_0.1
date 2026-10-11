from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field

# --- User & Authentication Schemas ---
class UserRegisterRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    full_name: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    id_token: str

class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str
    full_name: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    created_at: str

# --- Health & History Schemas ---
class HistorySaveRequest(BaseModel):
    analysis_id: str
    patient_summary: Dict[str, Any]
    disease_risks: List[Dict[str, Any]]
    clinvar_pathogenic_findings: List[Dict[str, Any]] = []
    pharmgkb_alerts: List[Dict[str, Any]] = []
    ai_explanation_narrative: str
    ai_lifestyle_prescriptions: List[str]
    pdf_report_base64: Optional[str] = None

class HistoryItemResponse(BaseModel):
    history_id: str
    user_id: str
    timestamp: str
    analysis_id: str
    patient_summary: Dict[str, Any]
    disease_risks: List[Dict[str, Any]]
    clinvar_pathogenic_findings: List[Dict[str, Any]] = []
    pharmgkb_alerts: List[Dict[str, Any]] = []
    ai_explanation_narrative: str
    ai_lifestyle_prescriptions: List[str]
    pdf_report_base64: Optional[str] = None

# --- Medical AI Agent Chatbot Schemas ---
class AgentChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []
    patient_context: Optional[Dict[str, Any]] = None
    language: str = "en"

class AgentChatResponse(BaseModel):
    reply: str
    intent_detected: str  # "medical_faq", "home_remedy", "emergency_hospital", "govt_scheme", "general"
    citations: List[Dict[str, str]] = []
    suggested_actions: List[str] = []
    timestamp: str

# --- Core Genomics & Clinical Models ---
class LifestyleFactors(BaseModel):
    age: int = Field(default=45, ge=18, le=100, description="Age in years")
    sex: str = Field(default="male", description="'male', 'female', or 'other'")
    bmi: float = Field(default=26.5, ge=12.0, le=60.0, description="Body Mass Index (kg/m²)")
    smoking_status: str = Field(default="never", description="'never', 'former', or 'current'")
    physical_activity_hours_per_week: float = Field(default=2.5, ge=0.0, le=40.0, description="Activity hours/week")
    mediterranean_diet_score: int = Field(default=6, ge=0, le=10, description="Adherence score (0-10)")
    systolic_bp: int = Field(default=120, ge=80, le=240, description="Systolic Blood Pressure (mmHg)")
    diastolic_bp: Optional[int] = Field(default=80, ge=40, le=140, description="Diastolic Blood Pressure (mmHg)")
    sleep_hours: float = Field(default=7.0, ge=3.0, le=14.0, description="Average sleep hours per night")
    alcohol_drinks_per_week: float = Field(default=2.0, ge=0.0, le=70.0, description="Standard alcoholic drinks per week")
    family_history_cad: bool = Field(default=False)
    family_history_t2d: bool = Field(default=False)
    family_history_ad: bool = Field(default=False)

class GenotypeVariant(BaseModel):
    rsid: str
    chromosome: Optional[str] = None
    position: Optional[int] = None
    ref_allele: Optional[str] = None
    alt_allele: Optional[str] = None
    dosage: float = Field(..., ge=0.0, le=2.0)

class ClinVarAnnotation(BaseModel):
    rsid: str
    gene: str
    clinical_significance: str
    review_status: str
    phenotype: str
    accession: str

class PharmGKBAnnotation(BaseModel):
    rsid: str
    gene: str
    drug: str
    phenotype_category: str
    clinical_recommendation: str
    level_of_evidence: str

class DiseaseRiskResult(BaseModel):
    disease_id: str
    disease_name: str
    prs_raw_score: float
    prs_standardized_z: float
    prs_percentile: float
    snps_found: int
    snps_total: int
    confidence_score: float
    fused_relative_risk: float
    fused_absolute_risk_10yr: float
    risk_category: str
    genetic_contribution_pct: float
    lifestyle_contribution_pct: float
    shap_mode: str
    shap_feature_importance: Dict[str, float]
    shap_waterfall_plot_b64: Optional[str] = None
    key_risk_drivers: List[str] = []

class AnalysisRequest(BaseModel):
    lifestyle: LifestyleFactors
    genomic_data: Optional[Dict[str, float]] = None
    language: str = "en"

class SimulationRequest(BaseModel):
    disease_id: str
    base_prs_percentile: float
    base_prs_z: float = 0.0
    lifestyle: LifestyleFactors

class SimulationResponse(BaseModel):
    disease_id: str
    simulated_relative_risk: float
    simulated_absolute_risk_10yr: float
    risk_delta_pct: float
    simulated_category: str
    actionable_levers: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    question: str
    report_summary: Dict[str, Any]
    language: str = "en"

class ChatResponse(BaseModel):
    answer: str
    citations: List[Dict[str, str]]
    timestamp: str

class SupportedPanelItem(BaseModel):
    rsid: str
    gene: str
    disease_id: str
    chromosome: str
    position: int
    effect_allele: str
    other_allele: str
    beta: float
    maf: float
    p_value: float

class AnalysisResponse(BaseModel):
    analysis_id: str
    timestamp: str
    patient_summary: Dict[str, Any]
    disease_risks: List[DiseaseRiskResult]
    clinvar_pathogenic_findings: List[ClinVarAnnotation]
    pharmgkb_alerts: List[PharmGKBAnnotation]
    ai_explanation_narrative: str
    ai_lifestyle_prescriptions: List[str]
    evidence_citations: List[Dict[str, str]]
    pdf_report_base64: Optional[str] = None
    system_status: Dict[str, Any]
