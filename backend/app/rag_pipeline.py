import os
import time
import logging
from typing import List, Dict, Any, Optional, Tuple

from app.config import settings
from app.terminal_logger import (
    log_checkpoint, log_qdrant_retrieval, log_groq_synthesis, print_banner
)

logger = logging.getLogger("generisk.rag")

DEFAULT_KNOWLEDGE_CHUNKS = [
    {
        "id": "cad_01",
        "disease_id": "cad",
        "topic": "CAD Pathophysiology & Genetics",
        "title": "AHA/ACC 2024 Guidelines on Polygenic Risk in Coronary Disease",
        "text": "Coronary Artery Disease (CAD) has an estimated polygenic heritability of 40-50%. Variants at chromosome 9p21.3 (e.g. rs1333049) and lipid loci (APOB rs693, PCSK9 rs11591147, LPA rs10455872) alter smooth muscle proliferation and LDL clearance. Top quintile PRS confers a 2.3-fold increased lifetime myocardial infarction hazard.",
        "citation": "AHA/ACC Cardiovascular Prevention Guidelines 2024; Circulation 149(4)",
        "video_url": "https://www.youtube.com/watch?v=3_PYnWVoUzM",
        "pmid": "38451296"
    },
    {
        "id": "cad_02",
        "disease_id": "cad",
        "topic": "CAD Lifestyle Interventions",
        "title": "AHA Life's Essential 8 - Coronary Risk Modification",
        "text": "Adherence to favorable lifestyle factors (no smoking, BMI < 25, regular aerobic exercise, Mediterranean diet) reduces coronary events by nearly 50% across all genetic strata, including patients in the highest genetic risk decile (Khera et al., NEJM).",
        "citation": "Khera AV et al. Genetic Risk, Adherence to a Healthy Lifestyle, and Coronary Disease. NEJM 2016; 375:2349-2358",
        "video_url": "https://www.youtube.com/watch?v=3_PYnWVoUzM",
        "pmid": "27846272"
    },
    {
        "id": "t2d_01",
        "disease_id": "t2d",
        "topic": "Type 2 Diabetes Genetics & Pancreatic Function",
        "title": "ADA 2024 Standards of Care: Polygenic Architecture of T2D",
        "text": "Type 2 Diabetes risk is strongly influenced by beta-cell transcription factor TCF7L2 rs7903146, which impairs GLP-1 induced insulin secretion. Additional risk alleles at KCNJ11 (rs5215) and PPARG (rs1801282) modulate peripheral insulin sensitivity and adipose storage.",
        "citation": "ADA Standards of Medical Care in Diabetes 2024; Diabetes Care 47(Suppl 1):S1-S343",
        "video_url": "https://www.youtube.com/watch?v=JAjZv41iUJU",
        "pmid": "38078580"
    },
    {
        "id": "t2d_02",
        "disease_id": "t2d",
        "topic": "T2D Lifestyle Mitigation & Diabetes Reversal",
        "title": "Diabetes Prevention Program (DPP) Outcomes Study",
        "text": "Intensive lifestyle intervention (achieving 7% weight reduction and 150 min/wk moderate physical activity) reduces Type 2 Diabetes incidence by 58% in high-risk individuals, outperforming metformin monotherapy (31%). Early prediabetes is reversible with low-glycemic nutrition.",
        "citation": "DPP Research Group. Reduction in the Incidence of Type 2 Diabetes with Lifestyle Intervention. NEJM 2002; 346:393-403",
        "video_url": "https://www.youtube.com/watch?v=JAjZv41iUJU",
        "pmid": "11832527"
    },
    {
        "id": "cancer_01",
        "disease_id": "breast_cancer",
        "topic": "Breast & Ovarian Cancer Prevention & Screening",
        "title": "NCCN 2024 Clinical Guidelines: Genetic/Familial High-Risk Cancer Screening",
        "text": "Pathogenic variants in BRCA1 (rs80357906) and BRCA2 (rs80359550) confer a 60-80% lifetime breast cancer risk and 20-40% ovarian cancer risk. General population screening: Annual or biennial mammography starting at age 40. High-risk carriers: Annual breast MRI + mammography starting at age 25-30. RED FLAG WARNINGS: Hard, painless breast lump, nipple inversion, bloody discharge, skin dimpling, axillary lymph node swelling.",
        "citation": "NCCN Clinical Practice Guidelines in Oncology: Genetic/Familial High-Risk Assessment 2024",
        "video_url": "https://www.youtube.com/watch?v=BmFEoCFDi-w",
        "pmid": "37841122"
    },
    {
        "id": "cancer_02",
        "disease_id": "cancer",
        "topic": "Colorectal Cancer Early Detection & Lynch Syndrome",
        "title": "US Multi-Society Task Force on Colorectal Cancer Screening",
        "text": "Colorectal cancer screening is recommended starting at age 45 for average-risk adults via colonoscopy (every 10 years) or annual fecal immunochemical test (FIT). Lynch syndrome (MLH1, MSH2, MSH6, PMS2) requires colonoscopy every 1-2 years starting at age 20-25. RED FLAG WARNINGS: Rectal bleeding or dark tarry stool, unexplained persistent change in bowel habits (>4 weeks), unintended weight loss, chronic crampy abdominal pain.",
        "citation": "USMSTF Colorectal Cancer Screening Guidelines 2023; Gastroenterology 164(5):1150-1168",
        "video_url": "https://www.youtube.com/watch?v=BmFEoCFDi-w",
        "pmid": "34045050"
    },
    {
        "id": "cancer_03",
        "disease_id": "cancer",
        "topic": "Lung & Oral Cancer Prevention: Tobacco Carcinogenesis",
        "title": "USPSTF Screening for Lung Cancer & WHO Global Tobacco Report",
        "text": "Tobacco smoke contains over 70 established carcinogens (including benzopyrene and NNK) that directly mutate the TP53 and KRAS tumor suppressor genes. Annual Low-Dose CT (LDCT) is recommended for adults aged 50-80 with a 20 pack-year smoking history. Smoking cessation halts further DNA adduct accumulation and cuts lung cancer risk by 50% after 10 years.",
        "citation": "USPSTF Recommendation Statement: Screening for Lung Cancer. JAMA 2021; 325(10):962-970",
        "video_url": "https://www.youtube.com/watch?v=BmFEoCFDi-w",
        "pmid": "33687448"
    },
    {
        "id": "stroke_01",
        "disease_id": "htn",
        "topic": "Acute Stroke Recognition & Golden Hour Triage",
        "title": "AHA/ASA Guidelines for the Early Management of Acute Ischemic Stroke",
        "text": "Stroke is a medical emergency where 1.9 million neurons die every minute of ischemia. Use the B.E. F.A.S.T. mnemonic: Balance loss, Eyesight blurring, Face drooping, Arm weakness, Speech slurred/difficulty, Time to call 108/112 immediately. Intravenous thrombolysis (tPA) is effective when administered within the 4.5-hour golden window.",
        "citation": "AHA/ASA Acute Ischemic Stroke Guidelines 2023; Stroke 54(7):e314-e344",
        "video_url": "https://www.youtube.com/watch?v=-NJm4TJ2it0",
        "pmid": "31662094"
    },
    {
        "id": "ad_01",
        "disease_id": "ad",
        "topic": "Alzheimer's Disease Genetics & Cognitive Reserve",
        "title": "NIA/Alzheimer's Association Consensus on APOE and Polygenic Factors",
        "text": "APOE epsilon-4 allele (defined by rs429358 and rs7412) increases Alzheimer's risk 3-fold (heterozygous) and 8-12 fold (homozygous). Additional polygenic contributions from CLU, CR1, and BIN1 modulate amyloid-beta clearance kinetics. The Lancet Commission identifies 14 modifiable risk factors (including hypertension control, cognitive training, hearing protection, social engagement, and physical activity) that prevent or delay up to 45% of dementia cases.",
        "citation": "Lancet Neurology Commission on Dementia Prevention 2024; Lancet 404:572-628",
        "video_url": "https://www.youtube.com/watch?v=yJXTXN4xrI8",
        "pmid": "39096924"
    },
    {
        "id": "htn_01",
        "disease_id": "htn",
        "topic": "Hypertension Polygenic Architecture & Organ Damage",
        "title": "ESC/ESH Guidelines for the Management of Arterial Hypertension",
        "text": "Essential hypertension is governed by multi-locus variants in renin-angiotensin-aldosterone signaling (AGT, CYP11B2) and NOS3. Sodium restriction (<2g/day), DASH dietary pattern, potassium supplementation, and aerobic exercise reduce SBP by 8-14 mmHg, counteracting genetic susceptibility and protecting against left ventricular hypertrophy and renal microalbuminuria.",
        "citation": "2023 ESH Guidelines for the management of arterial hypertension. J Hypertens 41(12):1874-2071",
        "video_url": "https://www.youtube.com/watch?v=Ab9OZsDECZw",
        "pmid": "37345492"
    },
    {
        "id": "pgx_01",
        "disease_id": "pgx",
        "topic": "Pharmacogenomics Guidelines & Precision Prescribing",
        "title": "CPIC Guidelines for CYP2C19, SLCO1B1, and VKORC1",
        "text": "CPIC recommends alternative antiplatelet therapy (prasugrel/ticagrelor) for CYP2C19 intermediate/poor metabolizers on clopidogrel. For SLCO1B1 rs4149056 carriers, high-dose simvastatin causes statin-associated muscle symptoms, warranting rosuvastatin/pravastatin alternatives. DPYD variant carriers must have 5-FU/capecitabine chemotherapy doses reduced by 50% to prevent fatal toxicity.",
        "citation": "CPIC Guidelines for Clopidogrel & Statins; Clin Pharmacol Ther 2022; 112(5):959-967",
        "video_url": "https://www.youtube.com/watch?v=XBe4jvvbpQc",
        "pmid": "35834882"
    },
    {
        "id": "covid19_01",
        "disease_id": "covid19",
        "topic": "COVID-19 Host Genetics & Severe Disease Risk",
        "title": "COVID-19 Host Genetics Initiative",
        "text": "Genetic susceptibility to severe COVID-19 is strongly linked to a cluster on chromosome 3 (rs11385942, LZTFL1/SLC6A20) and the ABO blood group locus (rs657152). Blood group A is associated with higher risk of respiratory failure, while blood group O is protective. Vaccination and early antiviral therapies (Paxlovid) drastically reduce mortality regardless of genetic risk.",
        "citation": "COVID-19 Host Genetics Initiative, Nature 2021; 600:472-477",
        "video_url": "https://www.youtube.com/watch?v=XBe4jvvbpQc",
        "pmid": "33067605"
    },
    {
        "id": "hiv_01",
        "disease_id": "hiv",
        "topic": "HIV-1 Genetic Resistance & CCR5 Mutation",
        "title": "CCR5-Delta32 and HIV-1 Immunity",
        "text": "The CCR5-delta32 mutation (rs333) results in a non-functional CCR5 co-receptor on CD4 T-cells. Individuals homozygous for this mutation are highly resistant to HIV-1 infection. Heterozygotes show delayed progression to AIDS. This genetic discovery led to the development of CCR5 inhibitor drugs (Maraviroc) for HIV treatment.",
        "citation": "Samson M et al. Resistance to HIV-1 infection in Caucasian individuals bearing mutant alleles of the CCR5 chemokine receptor gene. Nature 1996; 382:722-725",
        "video_url": "",
        "pmid": "8751444"
    },
    {
        "id": "asthma_01",
        "disease_id": "asthma",
        "topic": "Asthma Genetics & Precision Medicine",
        "title": "GINA Guidelines for Asthma Management",
        "text": "Asthma has a strong genetic component, particularly variants in IL1RL1 (rs1420101) and GSDMB (rs2305480). Precision management includes avoiding triggers (smoke, allergens) and using inhaled corticosteroids. Biologic therapies targeting Type 2 inflammation (e.g., anti-IL5, anti-IgE) are highly effective for severe genetic phenotypes.",
        "citation": "Global Initiative for Asthma (GINA) Strategy 2024",
        "video_url": "",
        "pmid": "24451229"
    }
]

class RagPipeline:
    def __init__(self):
        self.qdrant_client = None
        self.embedder = None
        self.qdrant_status = "uninitialized"
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.total_points_count = 0
        self.pubmed_points_count = 0
        self._init_qdrant()
        self._init_fastembed()
        self._init_groq()

    def _init_qdrant(self):
        """Connects to Qdrant Cloud and validates collection major_project without deleting points."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http.models import Distance, VectorParams

            if settings.QDRANT_URL:
                self.qdrant_client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                    timeout=8.0
                )
                logger.info(f"Connected to Qdrant Cloud. Target collection: '{self.collection_name}'.")
            else:
                self.qdrant_client = QdrantClient(":memory:")
                logger.info("Initialized in-memory Qdrant client.")

            # Validate existing collection
            existing_cols = [c.name for c in self.qdrant_client.get_collections().collections]
            if self.collection_name in existing_cols:
                info = self.qdrant_client.get_collection(self.collection_name)
                self.total_points_count = self.qdrant_client.count(self.collection_name).count
                self.qdrant_status = "connected"
                logger.info(
                    f"Verified Qdrant collection '{self.collection_name}': {self.total_points_count} points preserved."
                )
            else:
                # Create collection if missing with 384-dim cosine config
                logger.info(f"Collection '{self.collection_name}' not found. Creating collection (384-dim Cosine)...")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                self.qdrant_status = "connected"
        except Exception as e:
            logger.warning(f"Qdrant connection check failed: {e}. Utilizing fallback retrieval.")
            self.qdrant_status = f"unavailable: {e}"

    def _init_fastembed(self):
        try:
            from fastembed import TextEmbedding
            self.embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            logger.info("Initialized FastEmbed (bge-small-en-v1.5) ONNX engine.")
        except Exception as e:
            logger.warning(f"FastEmbed initialization deferred: {e}")
            self.embedder = None

    def _init_groq(self):
        self.groq_client = None
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info(f"Connected to Groq client. Primary model: {settings.GROQ_MODEL}")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

    def retrieve_relevant_evidence(self, query: str, top_k: int = 4) -> Tuple[List[Dict[str, Any]], str]:
        """
        Retrieves top-k evidence points from Qdrant collection major_project.
        Returns:
            (results_list, rag_source="qdrant" | "local_fallback")
        """
        results = []
        rag_source = "local_fallback"

        if self.qdrant_client and self.embedder and self.qdrant_status == "connected":
            try:
                existing_cols = [c.name for c in self.qdrant_client.get_collections().collections]
                if self.collection_name in existing_cols:
                    # In newer qdrant-client >= 1.10+, query_points is used with named vector
                    using_vector = "fast-bge-small-en-v1.5"
                    try:
                        col_info = self.qdrant_client.get_collection(self.collection_name)
                        vectors_cfg = col_info.config.params.vectors
                        if isinstance(vectors_cfg, dict) and vectors_cfg:
                            using_vector = list(vectors_cfg.keys())[0]
                        else:
                            using_vector = None
                    except Exception:
                        using_vector = "fast-bge-small-en-v1.5"

                    query_embeddings = list(self.embedder.embed([query]))
                    query_vector = query_embeddings[0].tolist()

                    if hasattr(self.qdrant_client, "query_points"):
                        query_kwargs = {
                            "collection_name": self.collection_name,
                            "query": query_vector,
                            "limit": top_k
                        }
                        if using_vector:
                            query_kwargs["using"] = using_vector
                        q_res = self.qdrant_client.query_points(**query_kwargs)
                        hits = q_res.points
                    elif hasattr(self.qdrant_client, "search"):
                        hits = self.qdrant_client.search(
                            collection_name=self.collection_name,
                            query_vector=query_vector,
                            limit=top_k
                        )
                    else:
                        hits = []

                    for hit in hits:
                        if not hit.payload:
                            continue
                        p = hit.payload
                        # Normalize payload across PubMed format and default knowledge format
                        title = p.get("title") or p.get("topic") or (p.get("document", "")[:60] + "...")
                        doc_text = p.get("document") or p.get("text") or ""
                        citation = p.get("citation") or (f"{p.get('journal', 'PubMed')} ({p.get('publication_year', '2024')})" if p.get("source") == "PubMed" else "Clinical Reference")
                        url = p.get("url") or p.get("video_url") or (f"https://pubmed.ncbi.nlm.nih.gov/{p.get('pmid')}/" if p.get("pmid") else "")
                        pmid = str(p.get("pmid", ""))

                        results.append({
                            "title": title,
                            "text": doc_text,
                            "citation": citation,
                            "url": url,
                            "video_url": p.get("video_url", ""),
                            "pmid": pmid,
                            "source": p.get("source", "Qdrant Vector DB"),
                            "disease": p.get("disease", "")
                        })

                    if results:
                        rag_source = "qdrant"
            except Exception as ex:
                logger.warning(f"Qdrant search error: {ex}")

        # Fallback to local default knowledge chunks
        if not results:
            rag_source = "local_fallback"
            q_tokens = set(query.lower().split())
            scored = []
            for chunk in DEFAULT_KNOWLEDGE_CHUNKS:
                text_tokens = set((chunk["topic"] + " " + chunk["text"]).lower().split())
                overlap = len(q_tokens.intersection(text_tokens))
                scored.append((overlap, chunk))
            scored.sort(key=lambda x: x[0], reverse=True)
            for _, c in scored[:top_k]:
                results.append({
                    "title": c["title"],
                    "text": c["text"],
                    "citation": c["citation"],
                    "url": c.get("video_url", ""),
                    "video_url": c.get("video_url", ""),
                    "pmid": c.get("pmid", ""),
                    "source": "Local Guidelines"
                })

        log_qdrant_retrieval(query=query, chunks_found=len(results), mode=rag_source)
        return results, rag_source

    def generate_explanation(
        self,
        patient_summary: Dict[str, Any],
        disease_risks: List[Dict[str, Any]],
        clinvar_findings: List[Dict[str, Any]],
        pharmgkb_alerts: List[Dict[str, Any]],
        language: str = "en"
    ) -> Tuple[str, List[str], List[Dict[str, str]], Dict[str, Any]]:
        """
        Synthesizes clinical narrative grounded strictly in calculated scores and Qdrant evidence.
        Returns:
            (narrative, prescriptions, citations, rag_meta)
        """
        t0 = time.time()
        log_checkpoint(1, 3, f"Retrieving Clinical Evidence from Qdrant '{self.collection_name}'")

        elevated_diseases = [d["disease_name"] for d in disease_risks if d.get("risk_category") in ("Elevated", "High")]
        context_query = f"Genomics and lifestyle risk management for {', '.join(elevated_diseases or ['cardiovascular disease', 'metabolic health', 'cancer'])}"

        evidence_chunks, rag_source = self.retrieve_relevant_evidence(context_query, top_k=4)
        citations = [
            {
                "title": c["title"],
                "citation": c["citation"],
                "url": c.get("url", ""),
                "video_url": c.get("video_url", ""),
                "pmid": c.get("pmid", "")
            }
            for c in evidence_chunks
        ]

        log_checkpoint(2, 3, "Synthesizing Grounded Explanation via Groq Multi-Model Engine")

        # Try Primary Groq Model and Configured Fallback Models
        models_to_try = [settings.GROQ_MODEL] + [m for m in settings.GROQ_FALLBACK_MODELS if m != settings.GROQ_MODEL]
        groq_success = False
        final_model_used = None
        fallback_reason = None

        if self.groq_client and settings.GROQ_API_KEY:
            for model_candidate in models_to_try:
                try:
                    system_prompt = (
                        "You are GeneRisk AI, an empathetic, evidence-based genomic medicine assistant. "
                        "Synthesize the user's multi-disease polygenic risk scores, lifestyle factors, and retrieved clinical literature. "
                        "Strict Rules:\n"
                        "1. Base your assertions strictly on the calculated numbers provided; DO NOT alter or recalculate risk percentages.\n"
                        "2. Explain genetic susceptibility clearly without fatalism (genes convey susceptibility, not destiny).\n"
                        "3. Contrast genetic PRS with modifiable lifestyle factors.\n"
                        "4. Highlight any monogenic ClinVar or PharmGKB drug interactions.\n"
                        "5. Provide 3-4 specific, high-impact lifestyle prescriptions.\n"
                        f"6. Write the explanation in language: {language}."
                    )

                    evidence_text = "\n\n".join([f"[{c['title']}]: {c['text']}" for c in evidence_chunks])
                    user_content = (
                        f"Patient Age: {patient_summary.get('age')}, Sex: {patient_summary.get('sex')}, BMI: {patient_summary.get('bmi')}\n"
                        f"Lifestyle: Smoking={patient_summary.get('smoking_status')}, Activity={patient_summary.get('physical_activity')} hrs/wk, SBP={patient_summary.get('systolic_bp')} mmHg\n"
                        f"Disease Results:\n" +
                        "\n".join([f"- {d['disease_name']}: PRS Percentile={d['prs_percentile']}%, Category={d['risk_category']}, Fused 10-Yr Absolute Risk={d['fused_absolute_risk_10yr']*100:.1f}%" for d in disease_risks]) +
                        f"\n\nClinVar Pathogenic Variants: {len(clinvar_findings)}\n"
                        f"PharmGKB Drug Alerts: {len(pharmgkb_alerts)}\n\n"
                        f"Clinical Literature:\n{evidence_text}"
                    )

                    response = self.groq_client.chat.completions.create(
                        model=model_candidate,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        temperature=0.3,
                        max_tokens=900,
                        timeout=12.0
                    )
                    raw_text = response.choices[0].message.content
                    prescriptions = self._extract_prescriptions(raw_text)
                    groq_success = True
                    final_model_used = model_candidate

                    log_groq_synthesis(model_candidate, is_live=True, duration_sec=time.time() - t0)
                    log_checkpoint(3, 3, f"Grounded Report Generated via Groq ({model_candidate})")

                    rag_meta = {
                        "rag_source": rag_source,
                        "retrieved_documents": len(evidence_chunks),
                        "explanation_mode": "groq",
                        "model_used": final_model_used
                    }
                    return raw_text, prescriptions, citations, rag_meta

                except Exception as e:
                    logger.warning(f"Groq model candidate '{model_candidate}' failed: {e}. Trying fallback model...")
                    fallback_reason = str(e)

        # Deterministic High-Fidelity Synthesizer
        narrative, prescriptions = self._deterministic_synthesizer(
            patient_summary, disease_risks, clinvar_findings, pharmgkb_alerts, language
        )
        log_groq_synthesis(settings.GROQ_MODEL, is_live=False, duration_sec=time.time() - t0)
        log_checkpoint(3, 3, "Report Synthesized via High-Fidelity Deterministic Engine")

        rag_meta = {
            "rag_source": rag_source,
            "retrieved_documents": len(evidence_chunks),
            "explanation_mode": "deterministic_fallback",
            "fallback_reason": fallback_reason or "Groq API key not configured"
        }
        return narrative, prescriptions, citations, rag_meta

    def answer_question(
        self,
        question: str,
        report_summary: Dict[str, Any],
        language: str = "en"
    ) -> Tuple[str, List[Dict[str, str]], Dict[str, Any]]:
        evidence_chunks, rag_source = self.retrieve_relevant_evidence(question, top_k=3)
        citations = [{"title": c["title"], "citation": c["citation"], "url": c.get("url", ""), "pmid": c.get("pmid", "")} for c in evidence_chunks]

        models_to_try = [settings.GROQ_MODEL] + [m for m in settings.GROQ_FALLBACK_MODELS if m != settings.GROQ_MODEL]
        if self.groq_client and settings.GROQ_API_KEY:
            for model_candidate in models_to_try:
                try:
                    system_prompt = (
                        "You are GeneRisk AI Clinical Assistant. Answer the patient's question regarding their genetic report. "
                        "Be accurate, empathetic, and ground your answer strictly in the clinical context and evidence provided. "
                        f"Respond in language: {language}."
                    )
                    evidence_text = "\n\n".join([f"[{c['title']}]: {c['text']}" for c in evidence_chunks])
                    user_msg = f"Report Summary: {report_summary}\nEvidence: {evidence_text}\nQuestion: {question}"

                    res = self.groq_client.chat.completions.create(
                        model=model_candidate,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_msg}
                        ],
                        temperature=0.2,
                        max_tokens=600,
                        timeout=10.0
                    )
                    return res.choices[0].message.content, citations, {"rag_source": rag_source, "explanation_mode": "groq", "model_used": model_candidate}
                except Exception as ex:
                    logger.warning(f"Groq chat model '{model_candidate}' failed: {ex}")

        answer = (
            f"Based on your genomic risk profile and published medical guidelines: Genetic risk represents statistical "
            f"susceptibility, not certainty. Adherence to a healthy Mediterranean dietary pattern, regular aerobic exercise (150 min/wk), "
            f"and blood pressure regulation can offset up to 50% of the genetic hazard. Always review findings with your physician."
        )
        return answer, citations, {"rag_source": rag_source, "explanation_mode": "deterministic_fallback"}

    def answer_agent_chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        patient_context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Tuple[str, str, List[Dict[str, str]], List[str]]:
        intent = "medical_faq"
        suggested_actions = ["Explain My PRS Score", "Cancer Screening Precautions", "What is a VCF File?"]

        evidence_chunks, _ = self.retrieve_relevant_evidence(message, top_k=3)
        citations = [{"title": c["title"], "citation": c["citation"], "url": c.get("url", ""), "pmid": c.get("pmid", "")} for c in evidence_chunks]

        models_to_try = [settings.GROQ_MODEL] + [m for m in settings.GROQ_FALLBACK_MODELS if m != settings.GROQ_MODEL]
        if self.groq_client and settings.GROQ_API_KEY:
            for model_candidate in models_to_try:
                try:
                    system_prompt = (
                        "You are Dr. GeneRisk, a compassionate, expert AI Health Assistant. "
                        "You answer all medical related questions by users in a helpful and evidence-based manner. "
                        "Rules:\n"
                        "1. Base your answer on the provided medical evidence where applicable.\n"
                        "2. For emergency symptoms (e.g. acute chest pain), prioritize dialing emergency helplines (108, 112) immediately.\n"
                        "3. For home remedies, provide safe, natural habits with standard medical disclaimers.\n"
                        "4. For government schemes, explain coverage details (₹5 Lakh under PM-JAY, 50-90% discount at Jan Aushadhi) clearly.\n"
                        f"5. Respond fluently in language: {language}."
                    )

                    evidence_text = "\n\n".join([f"[{c['title']}]: {c['text']}" for c in evidence_chunks])
                    messages = [{"role": "system", "content": system_prompt}]
                    for h in conversation_history[-4:]:
                        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})

                    context_str = f"Patient context: {patient_context}\n" if patient_context else ""
                    messages.append({"role": "user", "content": f"{context_str}Medical Evidence:\n{evidence_text}\n\nUser query: {message}"})

                    res = self.groq_client.chat.completions.create(
                        model=model_candidate,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=700,
                        timeout=10.0
                    )
                    return res.choices[0].message.content, intent, citations, suggested_actions
                except Exception as e:
                    logger.warning(f"Agent chat model '{model_candidate}' failed: {e}")

        # Fallback using answer_question if Groq fails
        dynamic_answer, rag_citations, _ = self.answer_question(message, {}, language)
        return dynamic_answer, intent, rag_citations, suggested_actions

    def _extract_prescriptions(self, text: str) -> List[str]:
        lines = text.split("\n")
        recs = []
        for line in lines:
            line_str = line.strip()
            if (line_str.startswith("- ") or line_str.startswith("* ") or (len(line_str) > 2 and line_str[0].isdigit() and line_str[1] in (".", ")"))) and len(line_str) > 15:
                clean_rec = line_str.lstrip("0123456789.-* ) ")
                if len(clean_rec) > 20:
                    recs.append(clean_rec)
        return recs[:4] if len(recs) >= 2 else [
            "Adopt an AHA/Mediterranean cardioprotective diet rich in omega-3s and fiber.",
            "Achieve at least 150-300 minutes per week of moderate-intensity aerobic exercise.",
            "Maintain optimal blood pressure below 120/80 mmHg via sodium moderation.",
            "Schedule annual metabolic lipid and fasting glucose screenings with your primary care provider."
        ]

    def _deterministic_synthesizer(
        self,
        patient: Dict[str, Any],
        risks: List[Dict[str, Any]],
        clinvar: List[Dict[str, Any]],
        pharmgkb: List[Dict[str, Any]],
        language: str
    ) -> Tuple[str, List[str]]:
        highest_risk = max(risks, key=lambda x: x.get("fused_absolute_risk_10yr", 0)) if risks else None

        narrative_parts = [
            f"### Clinical Genomic Risk Assessment Summary\n\n",
            f"Your genomic profile was evaluated across {len(risks)} polygenic disease models and high-penetrance variant databases. "
        ]

        if highest_risk:
            d_name = highest_risk.get("disease_name", "Cardiovascular")
            pct = highest_risk.get("prs_percentile", 50.0)
            cat = highest_risk.get("risk_category", "Average")
            ar = highest_risk.get("fused_absolute_risk_10yr", 0.08) * 100.0

            narrative_parts.append(
                f"Your highest calculated susceptibility is for **{d_name}**, placing your polygenic risk score at the **{pct:.1f}th population percentile** "
                f"with an overall **{cat}** 10-year risk category ({ar:.1f}% estimated absolute 10-year probability). "
            )

        if pharmgkb:
            narrative_parts.append(
                f"\n\n**Pharmacogenomics Alert:** We identified {len(pharmgkb)} actionable drug-gene interaction(s). "
                f"For example, genetic variation in *{pharmgkb[0].get('gene')}* affects metabolism of **{pharmgkb[0].get('drug')}** "
                f"({pharmgkb[0].get('clinical_recommendation')}). "
            )

        narrative_parts.append(
            "\n\nImportantly, polygenic risk is not deterministic. Landmark trials (such as the UK Biobank and DPP studies) "
            "confirm that adherence to favorable lifestyle choices substantially mitigates genetic risk across all examined conditions."
        )

        prescriptions = [
            "Maintain adherence to a Mediterranean-style dietary pattern high in fiber and polyphenols.",
            "Engage in ≥150 minutes of moderate-to-vigorous aerobic activity weekly.",
            "Keep systolic blood pressure strictly regulated (<120 mmHg) through lifestyle and clinical oversight.",
            "Discuss identified pharmacogenomic considerations with your prescribing physician prior to medication adjustments."
        ]

        return "".join(narrative_parts), prescriptions

rag_pipeline = RagPipeline()
