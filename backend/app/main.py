import os
import json
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

from app.config import settings
from app.database import init_tables, fetch_all, fetch_one, db_manager
from app.mongo_db import mongo_service
from app.auth import (
    hash_password, verify_password, create_jwt_token,
    get_current_user, get_optional_user, verify_google_token, exchange_google_code_for_user
)
from app.govt_schemes import get_govt_schemes
from app.terminal_logger import (
    print_banner, log_checkpoint, log_gwas_calculation,
    log_clinvar_pharmgkb, log_shap_execution, log_auth_event,
    log_vcf_parsing_summary, log_lifestyle_fusion, log_shap_and_accuracy, log_report_generation,
    GREEN, RESET, CYAN, YELLOW, BOLD
)
from app.schemas import (
    AnalysisRequest, AnalysisResponse, LifestyleFactors,
    DiseaseRiskResult, SimulationRequest, SimulationResponse,
    ChatRequest, ChatResponse, SupportedPanelItem,
    UserRegisterRequest, UserLoginRequest, GoogleAuthRequest, AuthResponse, UserResponse,
    HistorySaveRequest, HistoryItemResponse, AgentChatRequest, AgentChatResponse
)
from app.vcf_parser import parse_vcf_stream, clean_genomic_input
from app.prs_engine import prs_engine
from app.clinvar_lookup import lookup_clinvar_variants
from app.pharmgkb_lookup import lookup_pharmgkb_variants
from app.lifestyle_fusion import fuse_genetic_and_lifestyle_risk, compute_lifestyle_multipliers
from app.shap_explainer import shap_explainer, ensure_models_ready
from app.rag_pipeline import rag_pipeline
from app.report_generator import generate_pdf_report
from app.pubmed_service import ensure_pubmed_knowledge_ready, pubmed_service
from app.clinvar_service import ensure_clinvar_ready
from app.gwas_service import ensure_gwas_ready

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("generisk.main")

# Initialize database tables and run automatic background readiness checks
init_tables()

import threading
def _async_startup_checks():
    ensure_clinvar_ready()
    ensure_gwas_ready()
    ensure_models_ready()
    ensure_pubmed_knowledge_ready()

threading.Thread(target=_async_startup_checks, daemon=True).start()

db_status = "Turso Cloud (Remote)" if db_manager.is_turso_active else "Local SQLite (Offline)"
print_banner(f"GeneRisk 2.0 AI Platform Active | DB: {db_status} | Qdrant: {settings.QDRANT_COLLECTION_NAME}")

# Print full algorithm validation & accuracy scores on startup
log_shap_and_accuracy(shap_explainer.metrics, None)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GeneRisk 2.0: AI-Powered Genomic Risk Intelligence & Public Health Portal"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Safe System Status Endpoint ---
@app.get("/api/v1/system/status")
@app.get("/health")
@app.get("/api/v1/health")
async def get_system_status():
    """Returns comprehensive, safe status information for Qdrant, Turso, PubMed, SHAP, and Groq without exposing secrets."""
    # Qdrant status
    qdrant_connected = rag_pipeline.qdrant_status == "connected"
    qdrant_total_points = rag_pipeline.total_points_count
    
    # Check PubMed points count and last sync state
    pubmed_sync = db_manager.get_sync_state("pubmed_knowledge")
    last_pubmed_sync = pubmed_sync.get("last_synced_at") if pubmed_sync else "Not synchronized"
    pubmed_pts_count = pubmed_sync.get("record_count", 0) if pubmed_sync else 0

    # Turso / Database status
    turso_connected = db_manager.is_turso_active
    gwas_sync = db_manager.get_sync_state("gwas_catalog")
    clinvar_sync = db_manager.get_sync_state("clinvar_variants")

    try:
        gwas_cnt = len(fetch_all("SELECT 1 FROM gwas_weights"))
    except Exception:
        gwas_cnt = 0

    try:
        clinvar_cnt = len(fetch_all("SELECT 1 FROM clinvar_variants"))
    except Exception:
        clinvar_cnt = 0

    # XGBoost & SHAP models
    loaded_models = list(shap_explainer.models.keys())
    shap_ready = len(loaded_models) >= 5

    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "qdrant": {
            "connected": qdrant_connected,
            "collection_name": settings.QDRANT_COLLECTION_NAME,
            "total_points": qdrant_total_points,
            "pubmed_points": pubmed_pts_count,
            "last_pubmed_sync": last_pubmed_sync
        },
        "turso": {
            "connected": turso_connected,
            "active_source": db_manager.last_used_source,
            "gwas_variants_count": gwas_cnt,
            "clinvar_variants_count": clinvar_cnt,
            "last_gwas_sync": gwas_sync.get("last_synced_at") if gwas_sync else "initial",
            "last_clinvar_sync": clinvar_sync.get("last_synced_at") if clinvar_sync else "initial"
        },
        "models": {
            "loaded_diseases": loaded_models,
            "shap_readiness": "real_shap" if shap_ready else "partial",
            "metrics": shap_explainer.metrics
        },
        "groq": {
            "configured_model": settings.GROQ_MODEL,
            "fallback_models": settings.GROQ_FALLBACK_MODELS,
            "api_key_configured": bool(settings.GROQ_API_KEY)
        },
        "mongodb": {
            "connected": mongo_service.is_connected
        }
    }

# --- User Authentication Endpoints ---
@app.post("/api/v1/auth/register", response_model=AuthResponse)
async def register_user(req: UserRegisterRequest):
    """Registers a new user."""
    clean_email = req.email.lower().strip()
    existing = mongo_service.find_user_by_email(clean_email)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    user_id = f"usr_{abs(hash(clean_email)) % 1000000}"
    user_doc = {
        "user_id": user_id,
        "email": clean_email,
        "password_hash": hash_password(req.password),
        "full_name": req.full_name,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    success = mongo_service.create_user(user_doc)
    if not success:
        raise HTTPException(status_code=500, detail="Could not create user account.")

    log_auth_event("Email/Password User Registration", clean_email, user_id, is_new=True)
    token = create_jwt_token({"sub": clean_email, "user_id": user_id})
    return AuthResponse(
        token=token,
        user_id=user_id,
        email=clean_email,
        full_name=req.full_name
    )

@app.post("/api/v1/auth/login", response_model=AuthResponse)
async def login_user(req: UserLoginRequest):
    """Authenticates a user and issues a JWT token."""
    clean_email = req.email.lower().strip()
    user = mongo_service.find_user_by_email(clean_email)
    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    user_id = user.get("user_id", "")
    log_auth_event("Email/Password Sign-In", clean_email, user_id, is_new=False)
    token = create_jwt_token({"sub": clean_email, "user_id": user_id})
    return AuthResponse(
        token=token,
        user_id=user_id,
        email=clean_email,
        full_name=user.get("full_name", "User")
    )

@app.post("/api/v1/auth/google", response_model=AuthResponse)
async def google_auth_login(req: GoogleAuthRequest):
    """Authenticates or auto-registers a user via Google Cloud OAuth ID Token."""
    google_user = verify_google_token(req.id_token)
    if not google_user or not google_user.get("email"):
        raise HTTPException(status_code=401, detail="Invalid or expired Google ID Token.")

    email = google_user["email"]
    user = mongo_service.find_user_by_email(email)
    is_new = False
    if not user:
        is_new = True
        user_id = f"usr_google_{abs(hash(email)) % 1000000}"
        user_doc = {
            "user_id": user_id,
            "email": email,
            "password_hash": "oauth_google_authenticated",
            "full_name": google_user.get("full_name", "Google User"),
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        mongo_service.create_user(user_doc)
        user = user_doc

    user_id = user.get("user_id", "")
    log_auth_event("Google OAuth 2.0 Login", email, user_id, is_new=is_new)
    token = create_jwt_token({"sub": email, "user_id": user_id})
    return AuthResponse(
        token=token,
        user_id=user_id,
        email=email,
        full_name=user.get("full_name", "Google User")
    )

@app.get("/api/v1/auth/google/url")
async def get_google_auth_url(prompt: str = ""):
    """
    Returns Google OAuth 2.0 authorization consent URL.
    - prompt='' or not provided: silent sign-in attempt (no consent screen if already authorized)
    - prompt='select_account': let user pick account
    - prompt='consent': force re-consent (for first-time or re-authorization)
    In real-world apps, we default to 'select_account' only when the user explicitly
    wants to switch accounts; otherwise Google remembers their session.
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail="GOOGLE_CLIENT_ID is not configured in backend/.env.")

    # Default: use 'select_account' so user can choose which Google account.
    # This does NOT force sign-out; if only one account is logged in Google re-uses it automatically.
    # Frontend should store the returned JWT in localStorage so the user stays signed in
    # across page reloads without re-triggering this OAuth flow.
    oauth_prompt = prompt if prompt in ("none", "select_account", "consent", "login") else "select_account"

    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_CALLBACK_URL}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline&"
        f"prompt={oauth_prompt}"
    )
    return {"auth_url": auth_url}

@app.get("/api/v1/auth/google/callback")
async def google_auth_callback(code: str):
    """Handles Google OAuth redirect callback with authorization code."""
    google_user = exchange_google_code_for_user(code)
    if not google_user or not google_user.get("email"):
        raise HTTPException(status_code=400, detail="Could not verify authorization code with Google.")
    
    email = google_user["email"]
    user = mongo_service.find_user_by_email(email)
    is_new = False
    if not user:
        is_new = True
        user_id = f"usr_google_{abs(hash(email)) % 1000000}"
        user_doc = {
            "user_id": user_id,
            "email": email,
            "password_hash": "oauth_google_authenticated",
            "full_name": google_user.get("full_name", "Google User"),
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        mongo_service.create_user(user_doc)
        user = user_doc

    user_id = user.get("user_id", "")
    log_auth_event("Google OAuth Redirect Callback", email, user_id, is_new=is_new)
    token = create_jwt_token({"sub": email, "user_id": user_id})
    redirect_target = f"{settings.FRONTEND_REDIRECT_URL}?token={token}&user_id={user_id}&email={email}&full_name={user.get('full_name', 'User')}"
    return RedirectResponse(url=redirect_target)

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the authenticated user profile."""
    return UserResponse(
        user_id=user.get("user_id", ""),
        email=user.get("email", ""),
        full_name=user.get("full_name", ""),
        created_at=user.get("created_at", "")
    )

@app.post("/api/v1/auth/refresh", response_model=AuthResponse)
async def refresh_token(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Silently refreshes a valid JWT without requiring the user to re-authenticate.
    Frontend calls this on app boot to restore session from a stored token.
    Like real-world apps (Gmail, etc.) — as long as the JWT is valid, the session is restored.
    """
    email = user.get("email", "")
    user_id = user.get("user_id", "")
    new_token = create_jwt_token({"sub": email, "user_id": user_id})
    log_auth_event("Token Refresh (Silent Sign-In)", email, user_id, is_new=False)
    return AuthResponse(
        token=new_token,
        user_id=user_id,
        email=email,
        full_name=user.get("full_name", "User")
    )

@app.post("/api/v1/auth/logout")
async def logout(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Explicit logout — instructs frontend to clear the stored JWT.
    JWT is stateless so server-side invalidation is not needed;
    the frontend simply removes the token from localStorage.
    """
    log_auth_event("User Sign-Out", user.get("email", ""), user.get("user_id", ""), is_new=False)
    return {"success": True, "message": "Signed out successfully. Please clear your local session token."}


# --- Analysis History Endpoints ---
@app.post("/api/v1/history/save")
async def save_history_item(
    req: HistorySaveRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Saves an analysis record to the user's history."""
    user_id = user.get("email", "guest") if user else "guest"
    history_doc = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **req.model_dump()
    }
    history_id = mongo_service.save_analysis_history(history_doc)
    print(f"\n[MONGODB ATLAS] History Record Saved: ID={history_id} for User={user_id}")
    return {"status": "saved", "history_id": history_id}

@app.get("/api/v1/history", response_model=List[HistoryItemResponse])
async def get_history(user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieves previous analyses for the authenticated user."""
    items = mongo_service.get_user_history(user_id=user.get("email", ""))
    return [HistoryItemResponse(**item) for item in items]

@app.delete("/api/v1/history/{history_id}")
async def delete_history(history_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Deletes a specific history record."""
    success = mongo_service.delete_history_item(history_id, user_id=user.get("email", ""))
    return {"status": "deleted" if success else "not_found"}

# --- Government Healthcare Schemes ---
@app.get("/api/v1/govt-schemes")
async def fetch_govt_schemes(lang: str = "en"):
    """Returns tri-lingual government schemes (English, Hindi, Kannada)."""
    schemes = get_govt_schemes(language=lang)
    print(f"\n[GOVERNMENT SCHEMES PORTAL] Querying Scheme Database for language: '{lang}' -> Returned {len(schemes)} verified public programs.")
    return schemes

# --- Medical AI Agent Chatbot ---
@app.post("/api/v1/agent-chat", response_model=AgentChatResponse)
async def medical_agent_chat(req: AgentChatRequest):
    """24/7 AI Health Assistant answering health queries, home remedies, emergency advice, and schemes."""
    print(f"\n[AI HEALTH CHATBOT] Message Received: '{req.message}' (Lang: {req.language})")
    reply, intent, citations, actions = rag_pipeline.answer_agent_chat(
        message=req.message,
        conversation_history=req.conversation_history,
        patient_context=req.patient_context,
        language=req.language
    )
    print(f"   * Intent Detected: {intent.upper()} -> Returned {len(citations)} citations, {len(actions)} suggested actions.")
    return AgentChatResponse(
        reply=reply,
        intent_detected=intent,
        citations=citations,
        suggested_actions=actions,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

# --- Supported Panel & Demo Samples ---
@app.get("/api/v1/supported-panel", response_model=List[SupportedPanelItem])
async def get_supported_panel():
    """Returns the currently active GWAS SNP panel for filtering."""
    panel = prs_engine.get_supported_panel()
    return [SupportedPanelItem(**p) for p in panel]

@app.get("/api/v1/demo-samples")
async def get_demo_samples():
    """Returns simplified, easy-to-understand clinical demo profiles for everyday users."""
    return [
        {
            "id": "sample_cad_high",
            "title": "Heart Health & Cholesterol Alert",
            "tag": "High Heart Risk",
            "description": "Family history of heart problems + high genetic risk combined with smoking and fast food habits.",
            "lifestyle": {
                "age": 52,
                "sex": "male",
                "bmi": 29.8,
                "smoking_status": "current",
                "physical_activity_hours_per_week": 1.0,
                "mediterranean_diet_score": 4,
                "systolic_bp": 142,
                "sleep_hours": 6.0,
                "alcohol_drinks_per_week": 8.0,
                "family_history_cad": True,
                "family_history_t2d": False,
                "family_history_ad": False
            },
            "genomic_data": {
                "rs1333049": 2.0,
                "rs693": 2.0,
                "rs10455872": 1.0,
                "rs7903146": 1.0,
                "rs4149056": 1.0,
                "rs429358": 0.0,
                "rs7412": 0.0
            }
        },
        {
            "id": "sample_t2d_elevated",
            "title": "Sugar & Metabolic Management",
            "tag": "Elevated Sugar Risk",
            "description": "High genetic diabetes susceptibility paired with overweight BMI and sedentary office routine.",
            "lifestyle": {
                "age": 46,
                "sex": "female",
                "bmi": 32.4,
                "smoking_status": "never",
                "physical_activity_hours_per_week": 0.5,
                "mediterranean_diet_score": 5,
                "systolic_bp": 130,
                "sleep_hours": 6.5,
                "alcohol_drinks_per_week": 2.0,
                "family_history_cad": False,
                "family_history_t2d": True,
                "family_history_ad": False
            },
            "genomic_data": {
                "rs7903146": 2.0,
                "rs5215": 2.0,
                "rs1801282": 0.0,
                "rs9939609": 2.0,
                "rs1333049": 0.0,
                "rs429358": 0.0
            }
        },
        {
            "id": "sample_healthy_baseline",
            "title": "Healthy Active Baseline",
            "tag": "Optimal Lifestyle",
            "description": "Balanced Mediterranean diet, daily aerobic fitness, normal blood pressure, and protective genetics.",
            "lifestyle": {
                "age": 42,
                "sex": "female",
                "bmi": 22.8,
                "smoking_status": "never",
                "physical_activity_hours_per_week": 4.5,
                "mediterranean_diet_score": 9,
                "systolic_bp": 116,
                "sleep_hours": 7.5,
                "alcohol_drinks_per_week": 1.0,
                "family_history_cad": False,
                "family_history_t2d": False,
                "family_history_ad": False
            },
            "genomic_data": {
                "rs1333049": 0.0,
                "rs693": 0.0,
                "rs7903146": 0.0,
                "rs429358": 0.0,
                "rs7412": 1.0,
                "rs11136000": 1.0
            }
        },
        {
            "id": "sample_pgx_warning",
            "title": "Medication Safety & Sensitivity Alert",
            "tag": "Medicine Alert",
            "description": "Identifies sensitive reaction to cholesterol-lowering Statins and blood thinner medications.",
            "lifestyle": {
                "age": 58,
                "sex": "male",
                "bmi": 27.0,
                "smoking_status": "former",
                "physical_activity_hours_per_week": 2.5,
                "mediterranean_diet_score": 7,
                "systolic_bp": 128,
                "sleep_hours": 7.5,
                "alcohol_drinks_per_week": 3.0,
                "family_history_cad": True,
                "family_history_t2d": False,
                "family_history_ad": False
            },
            "genomic_data": {
                "rs4244285": 1.0,  # CYP2C19 *2 Clopidogrel alert
                "rs4149056": 1.0,  # SLCO1B1 *5 Simvastatin alert
                "rs9923231": 1.0,  # VKORC1 Warfarin sensitivity
                "rs1333049": 1.0,
                "rs7903146": 0.0
            }
        }
    ]

# --- Main Genomic Risk Analysis Endpoint ---
@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_genomic_risk(request: Request):
    """Main analysis endpoint. Accepts JSON payload or multipart form with VCF upload."""
    content_type = request.headers.get("content-type", "")
    lifestyle: LifestyleFactors
    genomic_data: Dict[str, float] = {}
    language: str = "en"

    if "application/json" in content_type:
        try:
            body_dict = await request.json()
            req = AnalysisRequest(**body_dict)
            lifestyle = req.lifestyle
            genomic_data = clean_genomic_input(req.genomic_data)
            language = req.language
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON request body: {e}")
    elif "multipart/form-data" in content_type:
        try:
            form = await request.form()
            lifestyle_raw = form.get("lifestyle_json")
            if not lifestyle_raw or not isinstance(lifestyle_raw, str):
                raise HTTPException(status_code=400, detail="Missing 'lifestyle_json' in form data.")
            lifestyle = LifestyleFactors(**json.loads(lifestyle_raw))
            language = str(form.get("language", "en"))

            uploaded_file = form.get("file")
            if uploaded_file and hasattr(uploaded_file, "filename") and uploaded_file.filename:
                vcf_t0 = time.time()
                suffix = Path(uploaded_file.filename).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    content = await uploaded_file.read()
                    tmp.write(content)
                    tmp_path = Path(tmp.name)

                target_rsids = prs_engine.get_supported_rsids()
                genomic_data = parse_vcf_stream(tmp_path, target_rsids=target_rsids, delete_after=True)
                vcf_ms = (time.time() - vcf_t0) * 1000.0
                log_vcf_parsing_summary(uploaded_file.filename, len(content.split(b"\n")), len(genomic_data), len(target_rsids), vcf_ms)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse form data: {e}")
    else:
        try:
            body_dict = await request.json()
            req = AnalysisRequest(**body_dict)
            lifestyle = req.lifestyle
            genomic_data = clean_genomic_input(req.genomic_data)
            language = req.language
        except Exception:
            raise HTTPException(status_code=400, detail="Unsupported Content-Type.")

    import time
    start_time = time.time()
    
    print_banner(f"NEW GENOMIC RISK ANALYSIS | Patient: {lifestyle.age}yo {lifestyle.sex.upper()} | BMI {lifestyle.bmi} kg/m² | SBP {lifestyle.systolic_bp} mmHg")

    # 1. PRS Standardized Scoring
    prs_results = prs_engine.compute_all_prs(genomic_data)
    snps_found_count = max([p["snps_found"] for p in prs_results.values()]) if prs_results else 0
    total_snps_count = max([p["snps_total"] for p in prs_results.values()]) if prs_results else 0
    log_gwas_calculation(snps_found_count, total_snps_count, prs_results)

    # 2. ClinVar & PharmGKB Variant Matchers
    clinvar_annotations = lookup_clinvar_variants(genomic_data)
    pharmgkb_alerts = lookup_pharmgkb_variants(genomic_data)
    log_clinvar_pharmgkb(clinvar_annotations, pharmgkb_alerts)

    # 3. Late-Fusion & SHAP Explainability
    disease_risk_results: List[DiseaseRiskResult] = []
    primary_shap_mode = "real_shap"

    for d_id, prs_info in prs_results.items():
        fusion_info = fuse_genetic_and_lifestyle_risk(
            disease_id=d_id,
            prs_standardized_z=prs_info["standardized_z"],
            prs_percentile=prs_info["percentile"],
            lifestyle=lifestyle
        )

        shap_mode, shap_imp, waterfall_b64 = shap_explainer.explain(
            disease_id=d_id,
            prs_z=prs_info["standardized_z"],
            prs_percentile=prs_info["percentile"],
            lifestyle=lifestyle
        )
        primary_shap_mode = shap_mode

        risk_res = DiseaseRiskResult(
            disease_id=d_id,
            disease_name=prs_info.get("disease_name", d_id.upper()),
            prs_raw_score=prs_info["raw_score"],
            prs_standardized_z=prs_info["standardized_z"],
            prs_percentile=prs_info["percentile"],
            snps_found=prs_info["snps_found"],
            snps_total=prs_info["snps_total"],
            confidence_score=prs_info["confidence_score"],
            fused_relative_risk=fusion_info["fused_relative_risk"],
            fused_absolute_risk_10yr=fusion_info["fused_absolute_risk_10yr"],
            risk_category=fusion_info["risk_category"],
            genetic_contribution_pct=fusion_info["genetic_contribution_pct"],
            lifestyle_contribution_pct=fusion_info["lifestyle_contribution_pct"],
            shap_mode=shap_mode,
            shap_feature_importance=shap_imp,
            shap_waterfall_plot_b64=waterfall_b64,
            key_risk_drivers=fusion_info["key_risk_drivers"]
        )
        disease_risk_results.append(risk_res)

    disease_risk_results.sort(key=lambda x: x.fused_absolute_risk_10yr, reverse=True)

    # Log Lifestyle Fusion and Algorithm Accuracy / SHAP Benchmarks
    log_lifestyle_fusion(lifestyle, disease_risk_results)
    log_shap_and_accuracy(shap_explainer.metrics, disease_risk_results[0] if disease_risk_results else None)

    patient_dict = {
        "age": lifestyle.age,
        "sex": lifestyle.sex,
        "bmi": lifestyle.bmi,
        "smoking_status": lifestyle.smoking_status,
        "physical_activity": lifestyle.physical_activity_hours_per_week,
        "systolic_bp": lifestyle.systolic_bp,
        "diet_score": lifestyle.mediterranean_diet_score,
        "sleep_hours": lifestyle.sleep_hours
    }

    # 4. RAG Clinical Narrative
    narrative, prescriptions, citations, rag_meta = rag_pipeline.generate_explanation(
        patient_summary=patient_dict,
        disease_risks=[d.model_dump() for d in disease_risk_results],
        clinvar_findings=[c.model_dump() for c in clinvar_annotations],
        pharmgkb_alerts=[p.model_dump() for p in pharmgkb_alerts],
        language=language
    )

    # 5. In-Memory PDF Generation
    try:
        pdf_b64 = generate_pdf_report(
            patient_summary=patient_dict,
            disease_risks=[d.model_dump() for d in disease_risk_results],
            clinvar_findings=[c.model_dump() for c in clinvar_annotations],
            pharmgkb_alerts=[p.model_dump() for p in pharmgkb_alerts],
            explanation_narrative=narrative,
            prescriptions=prescriptions
        )
    except Exception as ex:
        logger.error(f"PDF generation error: {ex}")
        pdf_b64 = None

    analysis_id = f"GR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{abs(hash(str(patient_dict))) % 10000}"
    log_report_generation(len(pdf_b64) if pdf_b64 else 0, time.time() - start_time, analysis_id)

    return AnalysisResponse(
        analysis_id=analysis_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
        patient_summary=patient_dict,
        disease_risks=disease_risk_results,
        clinvar_pathogenic_findings=clinvar_annotations,
        pharmgkb_alerts=pharmgkb_alerts,
        ai_explanation_narrative=narrative,
        ai_lifestyle_prescriptions=prescriptions,
        evidence_citations=citations,
        pdf_report_base64=pdf_b64,
        system_status={
            "prs_mode": "P+T Standardized Normal CDF",
            "rag_source": rag_meta.get("rag_source", "qdrant"),
            "qdrant_collection": settings.QDRANT_COLLECTION_NAME,
            "retrieved_documents": rag_meta.get("retrieved_documents", len(citations)),
            "explanation_mode": rag_meta.get("explanation_mode", "groq"),
            "model_used": rag_meta.get("model_used", settings.GROQ_MODEL),
            "db_source": db_manager.last_used_source,
            "shap_mode": primary_shap_mode,
            "ephemeral_mode": "zero-disk-persistence active",
            "database_mode": "MongoDB Atlas / Document Store"
        }
    )

# --- Live What-If Simulator ---
@app.post("/api/v1/simulate", response_model=SimulationResponse)
async def simulate_lifestyle_modification(req: SimulationRequest):
    fusion = fuse_genetic_and_lifestyle_risk(
        disease_id=req.disease_id,
        prs_standardized_z=req.base_prs_z,
        prs_percentile=req.base_prs_percentile,
        lifestyle=req.lifestyle
    )

    avg_life = LifestyleFactors(
        age=req.lifestyle.age,
        sex=req.lifestyle.sex,
        bmi=25.0,
        smoking_status="never",
        physical_activity_hours_per_week=2.5,
        mediterranean_diet_score=7,
        systolic_bp=120,
        sleep_hours=7.5,
        alcohol_drinks_per_week=2.0
    )
    base_fusion = fuse_genetic_and_lifestyle_risk(
        disease_id=req.disease_id,
        prs_standardized_z=req.base_prs_z,
        prs_percentile=req.base_prs_percentile,
        lifestyle=avg_life
    )

    current_ar = fusion["fused_absolute_risk_10yr"]
    base_ar = base_fusion["fused_absolute_risk_10yr"]
    delta_pct = round(((current_ar - base_ar) / base_ar) * 100.0, 1)

    levers = []
    if req.lifestyle.smoking_status == "current":
        levers.append({"lever": "Smoking Cessation", "potential_reduction_pct": 35.0, "impact": "High"})
    if req.lifestyle.bmi > 26.0:
        levers.append({"lever": "Target 5-10% Weight Reduction", "potential_reduction_pct": 18.0, "impact": "High"})
    if req.lifestyle.physical_activity_hours_per_week < 2.5:
        levers.append({"lever": "Increase Activity to 150 min/wk", "potential_reduction_pct": 14.0, "impact": "Medium"})
    if req.lifestyle.systolic_bp > 125:
        levers.append({"lever": "Reduce SBP below 120 mmHg", "potential_reduction_pct": 20.0, "impact": "High"})

    return SimulationResponse(
        disease_id=req.disease_id,
        simulated_relative_risk=fusion["fused_relative_risk"],
        simulated_absolute_risk_10yr=fusion["fused_absolute_risk_10yr"],
        risk_delta_pct=delta_pct,
        simulated_category=fusion["risk_category"],
        actionable_levers=levers
    )

@app.get("/api/v1/download/sample-vcf/{filename}")
async def download_sample_vcf(filename: str):
    """Allows downloading pre-configured real benchmark sample VCF files."""
    sample_dir = Path(__file__).resolve().parent.parent.parent / "sample_vcf_data"
    file_path = sample_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample VCF file not found.")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="text/plain" if not filename.endswith(".gz") else "application/gzip"
    )

# --- Legacy Report Chat ---
@app.post("/api/v1/chat", response_model=ChatResponse)
async def report_followup_chat(req: ChatRequest):
    answer, citations, meta = rag_pipeline.answer_question(
        question=req.question,
        report_summary=req.report_summary,
        language=req.language
    )
    return ChatResponse(
        answer=answer,
        citations=citations,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
