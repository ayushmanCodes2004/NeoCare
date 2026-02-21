"""
FastAPI Server for Medical RAG System
Production-ready API for high-risk pregnancy detection
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime

from production_pipeline import ProductionRAGPipeline

# ============================================================
# API Models
# ============================================================

# ============================================================
# Structured Input Models
# ============================================================

class PatientInfo(BaseModel):
    """Patient demographic information."""
    patientId: Optional[str] = None
    name: Optional[str] = None
    age: int
    gravida: Optional[int] = None
    para: Optional[int] = None
    livingChildren: Optional[int] = None
    gestationalWeeks: Optional[int] = None
    lmpDate: Optional[str] = None
    estimatedDueDate: Optional[str] = None


class MedicalHistory(BaseModel):
    """Patient medical history."""
    previousLSCS: bool = False
    badObstetricHistory: bool = False
    previousStillbirth: bool = False
    previousPretermDelivery: bool = False
    previousAbortion: bool = False
    systemicIllness: Optional[str] = "None"
    chronicHypertension: bool = False
    diabetes: bool = False
    thyroidDisorder: bool = False
    # V2: Lifestyle
    smoking: bool = False
    tobaccoUse: bool = False
    alcoholUse: bool = False


class Vitals(BaseModel):
    """Patient vital signs."""
    weightKg: Optional[float] = None
    heightCm: Optional[float] = None
    bmi: Optional[float] = None
    bpSystolic: int
    bpDiastolic: int
    pulseRate: Optional[int] = None
    respiratoryRate: Optional[int] = None
    temperatureCelsius: Optional[float] = None
    pallor: bool = False
    pedalEdema: bool = False


class LabReports(BaseModel):
    """Laboratory test results."""
    hemoglobin: float
    plateletCount: Optional[int] = None
    bloodGroup: Optional[str] = None
    rhNegative: bool = False
    urineProtein: bool = False
    urineSugar: bool = False
    fastingBloodSugar: Optional[float] = None
    ogtt2hrPG: Optional[float] = None  # V2: OGTT 2-hour plasma glucose
    hivPositive: bool = False
    syphilisPositive: bool = False
    serumCreatinine: Optional[float] = None
    ast: Optional[int] = None
    alt: Optional[int] = None


class ObstetricHistory(BaseModel):
    """Obstetric history (V2)."""
    birthOrder: Optional[int] = None
    interPregnancyInterval: Optional[int] = None  # Months
    stillbirthCount: int = 0
    abortionCount: int = 0
    pretermHistory: bool = False


class PregnancyDetails(BaseModel):
    """Current pregnancy details."""
    twinPregnancy: bool = False
    malpresentation: bool = False
    placentaPrevia: bool = False
    reducedFetalMovement: bool = False
    amnioticFluidNormal: bool = True
    umbilicalDopplerAbnormal: bool = False


class CurrentSymptoms(BaseModel):
    """Current symptoms."""
    headache: bool = False
    visualDisturbance: bool = False
    epigastricPain: bool = False
    decreasedUrineOutput: bool = False
    bleedingPerVagina: bool = False
    convulsions: bool = False


class VisitMetadata(BaseModel):
    """Visit metadata."""
    visitType: Optional[str] = "Routine ANC"
    visitNumber: Optional[int] = None
    healthWorkerId: Optional[str] = None
    subCenterId: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    timestamp: Optional[str] = None


class StructuredData(BaseModel):
    """Complete structured patient data."""
    patient_info: PatientInfo
    medical_history: MedicalHistory
    vitals: Vitals
    lab_reports: LabReports
    obstetric_history: Optional[ObstetricHistory] = None  # V2
    pregnancy_details: PregnancyDetails
    current_symptoms: CurrentSymptoms
    visit_metadata: Optional[VisitMetadata] = None


class StructuredQueryRequest(BaseModel):
    """Request model for structured clinical data."""
    clinical_summary: str = Field(..., description="Brief clinical summary")
    structured_data: StructuredData
    care_level: Optional[str] = Field("PHC", description="Care level: ASHA, PHC, CHC, or DISTRICT")
    verbose: Optional[bool] = Field(False, description="Include debug information")
    
    class Config:
        schema_extra = {
            "example": {
                "clinical_summary": "36-year-old G3P1 at 30 weeks with severe anemia, hypertension, twin pregnancy",
                "structured_data": {
                    "patient_info": {
                        "age": 36,
                        "gravida": 3,
                        "para": 1,
                        "gestationalWeeks": 30
                    },
                    "medical_history": {
                        "previousLSCS": True,
                        "chronicHypertension": False
                    },
                    "vitals": {
                        "bpSystolic": 150,
                        "bpDiastolic": 100,
                        "pedalEdema": True
                    },
                    "lab_reports": {
                        "hemoglobin": 6.5,
                        "urineProtein": True
                    },
                    "pregnancy_details": {
                        "twinPregnancy": True,
                        "reducedFetalMovement": True
                    },
                    "current_symptoms": {
                        "headache": False
                    }
                },
                "care_level": "PHC"
            }
        }


# ============================================================
# Simple Query Models
# ============================================================

class QueryRequest(BaseModel):
    """Request model for clinical query."""
    query: str = Field(..., description="Clinical query about pregnancy case", min_length=10)
    care_level: Optional[str] = Field("PHC", description="Care level: ASHA, PHC, CHC, or DISTRICT")
    verbose: Optional[bool] = Field(False, description="Include debug information")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "38-year-old pregnant woman with BP 150/95, Hb 10.5, twin pregnancy",
                "care_level": "PHC",
                "verbose": False
            }
        }


class RiskFlag(BaseModel):
    """Individual risk flag."""
    condition: str
    present: bool
    severity: str
    value: str
    threshold: Optional[str] = None
    rationale: Optional[str] = None
    score: Optional[int] = None


class ClinicalFeatures(BaseModel):
    """Extracted clinical features."""
    age: Optional[int] = None
    gestational_age_weeks: Optional[int] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    hemoglobin: Optional[float] = None
    fbs: Optional[float] = None
    twin_pregnancy: bool = False
    prior_cesarean: bool = False
    placenta_previa: bool = False
    comorbidities: List[str] = []
    extraction_confidence: float = 0.0
    missing_fields: List[str] = []
    # V2: Anthropometric
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    # V2: Lifestyle
    smoking: bool = False
    tobacco_use: bool = False
    alcohol_use: bool = False
    # V2: Obstetric history
    birth_order: Optional[int] = None
    inter_pregnancy_interval: Optional[int] = None
    stillbirth_count: int = 0
    abortion_count: int = 0
    preterm_history: bool = False
    # V2: Serology
    rh_negative: bool = False
    hiv_positive: bool = False
    syphilis_positive: bool = False
    # V2: Complications
    malpresentation: bool = False
    systemic_illness: bool = False


class ConfidenceBreakdown(BaseModel):
    """Confidence score breakdown."""
    retrieval_quality: float
    rule_coverage: float
    chunk_agreement: float
    extractor_confidence: float


class Confidence(BaseModel):
    """Confidence information."""
    score: float
    level: str
    original_score: Optional[float] = None
    ceiling_applied: Optional[List[str]] = []
    breakdown: ConfidenceBreakdown


class RuleOutput(BaseModel):
    """Rule engine output."""
    overall_risk: str
    total_score: int
    rule_coverage: float
    triggered_rules: List[str]
    risk_flags: List[RiskFlag]


class RetrievalStats(BaseModel):
    """Retrieval statistics."""
    rewritten_query: str
    faiss_count: int
    bm25_count: int
    final_count: int
    retrieval_quality: float
    chunk_agreement: float


class QueryResponse(BaseModel):
    """Response model for clinical query."""
    success: bool
    query: str
    answer: str
    blocked: bool
    care_level: str
    confidence: Confidence
    features: ClinicalFeatures
    rule_output: RuleOutput
    retrieval_stats: Optional[RetrievalStats] = None
    timestamp: str
    processing_time_ms: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "query": "38-year-old with BP 150/95, Hb 10.5, twins",
                "answer": "[CLINICAL DECISION SUPPORT — NOT A DIAGNOSIS]...",
                "blocked": False,
                "care_level": "PHC",
                "confidence": {
                    "score": 0.75,
                    "level": "MEDIUM",
                    "breakdown": {
                        "retrieval_quality": 0.80,
                        "rule_coverage": 1.0,
                        "chunk_agreement": 0.70,
                        "extractor_confidence": 0.95
                    }
                },
                "features": {
                    "age": 38,
                    "systolic_bp": 150,
                    "diastolic_bp": 95,
                    "hemoglobin": 10.5,
                    "twin_pregnancy": True,
                    "extraction_confidence": 0.95
                },
                "rule_output": {
                    "overall_risk": "CRITICAL",
                    "total_score": 10,
                    "rule_coverage": 1.0,
                    "triggered_rules": ["advanced_maternal_age", "hypertension", "mild_anemia", "twin_pregnancy"]
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    system: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: str


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="Medical RAG API",
    description="Production-ready API for high-risk pregnancy detection using RAG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance (loaded once)
pipeline = None


# ============================================================
# Startup/Shutdown Events
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on startup."""
    global pipeline
    print("🚀 Starting Medical RAG API...")
    print("📦 Loading production pipeline...")
    try:
        pipeline = ProductionRAGPipeline()
        print("✅ Pipeline loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load pipeline: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 Shutting down Medical RAG API...")


# ============================================================
# API Endpoints
# ============================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "system": "Medical RAG - High-Risk Pregnancy Detection",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "system": "Medical RAG - High-Risk Pregnancy Detection",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process clinical query and return risk assessment.
    
    Args:
        request: QueryRequest with clinical query and options
        
    Returns:
        QueryResponse with risk assessment and recommendations
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    # Validate care level
    valid_care_levels = ["ASHA", "PHC", "CHC", "DISTRICT"]
    if request.care_level not in valid_care_levels:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid care_level. Must be one of: {', '.join(valid_care_levels)}"
        )
    
    try:
        # Start timing
        import time
        start_time = time.time()
        
        # Run pipeline
        result = pipeline.run(
            query=request.query,
            verbose=request.verbose,
            care_level=request.care_level
        )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Convert to response model
        response = QueryResponse(
            success=True,
            query=result['query'],
            answer=result['answer'],
            blocked=result['blocked'],
            care_level=request.care_level,
            confidence=Confidence(
                score=result['confidence']['score'],
                level=result['confidence']['level'],
                original_score=result['confidence'].get('original_score'),
                ceiling_applied=result['confidence'].get('ceiling_applied', []),
                breakdown=ConfidenceBreakdown(**result['confidence']['breakdown'])
            ),
            features=ClinicalFeatures(**result['features']),
            rule_output=RuleOutput(
                overall_risk=result['rule_output']['overall_risk'],
                total_score=result['rule_output']['total_score'],
                rule_coverage=result['rule_output']['rule_coverage'],
                triggered_rules=result['rule_output'].get('triggered_rules', []),
                risk_flags=[RiskFlag(**flag) for flag in result['rule_output']['risk_flags']]
            ),
            retrieval_stats=RetrievalStats(**result['retrieval_stats']) if not result['blocked'] else None,
            timestamp=datetime.utcnow().isoformat() + "Z",
            processing_time_ms=round(processing_time_ms, 2)
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/assess")
async def assess_risk_simple(request: QueryRequest):
    """
    Simplified risk assessment endpoint with clean JSON output.
    
    Returns a simplified structure:
    {
        "isHighRisk": true/false,
        "riskLevel": "LOW/MODERATE/HIGH/CRITICAL",
        "detectedRisks": ["Risk 1", "Risk 2", ...],
        "explanation": "Brief explanation of the assessment",
        "confidence": 0.0-1.0,
        "recommendation": "Clinical recommendation"
    }
    """
    try:
        # Process query
        result = pipeline.run(
            query=request.query,
            care_level=request.care_level,
            verbose=request.verbose
        )
        
        # Check if blocked
        if result['blocked']:
            return {
                "isHighRisk": False,
                "riskLevel": "UNKNOWN",
                "detectedRisks": [],
                "explanation": "Unable to assess risk due to insufficient evidence. Please provide more clinical details or consult a healthcare professional.",
                "confidence": 0.0,
                "recommendation": "Consult qualified healthcare professional for clinical assessment."
            }
        
        # Extract risk information
        rule_output = result['rule_output']
        overall_risk = rule_output['overall_risk']
        triggered_rules = rule_output.get('triggered_rules', [])
        
        # FIX 1: isHighRisk based on GoI master high-risk list (Section 13 + V2)
        # Source: clinical_thresholds.md Section 13 + COMPLETE_HPR_THRESHOLDS.md
        HIGH_RISK_CONDITIONS = [
            # Anaemia (only severe)
            "severe_anaemia",  # Hb < 7 g/dL (NOT mild or moderate)
            # Hypertension
            "pregnancy_induced_hypertension",
            "pre_eclampsia",
            "pre_eclamptic_toxemia",
            "severe_pre_eclampsia",
            "eclampsia",
            "chronic_hypertension",
            "hypertension",
            # GDM
            "gestational_diabetes_mellitus",
            "gdm_confirmed",
            # Thyroid
            "hypothyroidism",
            "hypothyroid_overt",
            "hypothyroid_subclinical",
            # Age
            "young_primi",  # < 20 years
            "elderly_gravida",  # > 35 years
            "advanced_maternal_age",
            # Pregnancy complications
            "twin_pregnancy",
            "multiple_pregnancy",
            "malpresentation",
            "placenta_previa",
            "low_lying_placenta",
            "iugr_suspected",
            # Obstetric history
            "previous_lscs",
            "previous_cs",
            "bad_obstetric_history",
            "previous_preterm",  # V2
            "previous_stillbirth",  # V2
            "previous_abortion",  # V2
            "high_birth_order",  # V2
            "short_birth_spacing",  # V2
            # Serology
            "rh_negative",
            "hiv_positive",
            "syphilis_positive",
            # Anthropometric (V2)
            "short_stature",  # Height < 140 cm
            "high_bmi",  # BMI >= 30
            # Lifestyle (V2)
            "smoking",
            "tobacco_use",
            "alcohol_use",
            # Systemic illness
            "systemic_illness_current_or_past",
            "systemic_illness"
        ]
        is_high_risk = any(rule in HIGH_RISK_CONDITIONS for rule in triggered_rules)
        
        # Extract detected risks from risk flags
        detected_risks = []
        for flag in rule_output.get('risk_flags', []):
            if flag.get('present', False):
                condition = flag['condition']
                # Clean up condition names
                if condition not in detected_risks:
                    detected_risks.append(condition)
        
        # Generate explanation from RAG answer (comprehensive)
        answer = result['answer']
        explanation = _generate_explanation(answer, detected_risks, overall_risk)
        
        # Extract recommendation from RAG answer based on explanation keywords
        recommendation = _extract_recommendation_from_rag(answer, explanation)
        
        # Get confidence
        confidence = result['confidence']['score']
        
        return {
            "isHighRisk": is_high_risk,
            "riskLevel": overall_risk,
            "detectedRisks": detected_risks,
            "explanation": explanation,
            "confidence": round(confidence, 2),
            "recommendation": recommendation
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/assess-structured")
async def assess_structured(request: StructuredQueryRequest):
    """
    Structured risk assessment endpoint with detailed patient data.
    
    Accepts structured JSON with patient demographics, vitals, labs, etc.
    Returns simplified risk assessment.
    
    This endpoint converts structured data into a clinical query for the RAG pipeline.
    """
    try:
        # Convert structured data to clinical query
        query = _build_clinical_query(request.structured_data, request.clinical_summary)
        
        # Debug: Print generated query
        print(f"\n{'='*70}")
        print(f"STRUCTURED INPUT CONVERTED TO QUERY:")
        print(f"{'='*70}")
        print(query)
        print(f"{'='*70}\n")
        
        # Process query
        result = pipeline.run(
            query=query,
            care_level=request.care_level,
            input_type="structured_json",  # FIX 2: Mark as structured JSON for confidence boost
            verbose=True  # Force verbose to see what's happening
        )
        
        # Check if blocked
        if result['blocked']:
            return {
                "isHighRisk": False,
                "riskLevel": "UNKNOWN",
                "detectedRisks": [],
                "explanation": "Unable to assess risk due to insufficient evidence. Please provide more clinical details or consult a healthcare professional.",
                "confidence": 0.0,
                "recommendation": "Consult qualified healthcare professional for clinical assessment.",
                "patientId": request.structured_data.patient_info.patientId,
                "visitMetadata": request.structured_data.visit_metadata.dict() if request.structured_data.visit_metadata else None
            }
        
        # Extract risk information
        rule_output = result['rule_output']
        overall_risk = rule_output['overall_risk']
        triggered_rules = rule_output.get('triggered_rules', [])
        
        # FIX 1: isHighRisk based on GoI master high-risk list (Section 13 + V2)
        # Source: clinical_thresholds.md Section 13 + COMPLETE_HPR_THRESHOLDS.md
        HIGH_RISK_CONDITIONS = [
            # Anaemia (only severe)
            "severe_anaemia",  # Hb < 7 g/dL (NOT mild or moderate)
            # Hypertension
            "pregnancy_induced_hypertension",
            "pre_eclampsia",
            "pre_eclamptic_toxemia",
            "severe_pre_eclampsia",
            "eclampsia",
            "chronic_hypertension",
            "hypertension",
            # GDM
            "gestational_diabetes_mellitus",
            "gdm_confirmed",
            # Thyroid
            "hypothyroidism",
            "hypothyroid_overt",
            "hypothyroid_subclinical",
            # Age
            "young_primi",  # < 20 years
            "elderly_gravida",  # > 35 years
            "advanced_maternal_age",
            # Pregnancy complications
            "twin_pregnancy",
            "multiple_pregnancy",
            "malpresentation",
            "placenta_previa",
            "low_lying_placenta",
            "iugr_suspected",
            # Obstetric history
            "previous_lscs",
            "previous_cs",
            "bad_obstetric_history",
            "previous_preterm",  # V2
            "previous_stillbirth",  # V2
            "previous_abortion",  # V2
            "high_birth_order",  # V2
            "short_birth_spacing",  # V2
            # Serology
            "rh_negative",
            "hiv_positive",
            "syphilis_positive",
            # Anthropometric (V2)
            "short_stature",  # Height < 140 cm
            "high_bmi",  # BMI >= 30
            # Lifestyle (V2)
            "smoking",
            "tobacco_use",
            "alcohol_use",
            # Systemic illness
            "systemic_illness_current_or_past",
            "systemic_illness"
        ]
        is_high_risk = any(rule in HIGH_RISK_CONDITIONS for rule in triggered_rules)
        
        # Extract detected risks
        detected_risks = []
        for flag in rule_output.get('risk_flags', []):
            if flag.get('present', False):
                condition = flag['condition']
                if condition not in detected_risks:
                    detected_risks.append(condition)
        
        # Generate explanation from RAG answer (comprehensive)
        answer = result['answer']
        explanation = _generate_explanation(answer, detected_risks, overall_risk)
        
        # Extract recommendation from RAG answer based on explanation keywords
        recommendation = _extract_recommendation_from_rag(answer, explanation)
        
        # Get confidence
        confidence = result['confidence']['score']
        
        # Build response with patient context
        response = {
            "isHighRisk": is_high_risk,
            "riskLevel": overall_risk,
            "detectedRisks": detected_risks,
            "explanation": explanation,
            "confidence": round(confidence, 2),
            "recommendation": recommendation,
            "patientId": request.structured_data.patient_info.patientId,
            "patientName": request.structured_data.patient_info.name,
            "age": request.structured_data.patient_info.age,
            "gestationalWeeks": request.structured_data.patient_info.gestationalWeeks,
            "visitMetadata": request.structured_data.visit_metadata.dict() if request.structured_data.visit_metadata else None
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing structured query: {str(e)}"
        )


# ============================================================
# FIX 3: RECOMMENDATION_MAP - Clean, isolated recommendations
# ============================================================

RECOMMENDATION_MAP = {
    "CRITICAL": "URGENT: Immediate referral to CEmOC/District Hospital required.",
    "HIGH": "Immediate obstetric consultation at FRU/CHC recommended.",
    "MODERATE": "Enhanced antenatal care with specialist consultation at CHC/PHC recommended.",
    "LOW": "Continue routine antenatal care with regular monitoring."
}


def _extract_recommendation_from_rag(rag_answer: str, explanation: str) -> str:
    """
    Generate clinical recommendation based on keywords in explanation.
    FIX 3: Uses RECOMMENDATION_MAP only - no RAG text, no page refs, max 200 chars.
    
    Args:
        rag_answer: Full RAG-generated answer (not used - kept for compatibility)
        explanation: Generated explanation text
        
    Returns:
        Clinical recommendation string from RECOMMENDATION_MAP
    """
    # FIX 3: Generate based on keywords in explanation using RECOMMENDATION_MAP ONLY
    explanation_lower = explanation.lower()
    
    # Check for risk level keywords in explanation
    if 'critical' in explanation_lower or 'emergency' in explanation_lower:
        return RECOMMENDATION_MAP["CRITICAL"]
    elif 'high' in explanation_lower and 'risk' in explanation_lower:
        return RECOMMENDATION_MAP["HIGH"]
    elif 'moderate' in explanation_lower:
        return RECOMMENDATION_MAP["MODERATE"]
    elif 'low' in explanation_lower or 'no significant risk' in explanation_lower:
        return RECOMMENDATION_MAP["LOW"]
    else:
        # Default: if any risk factors mentioned, use MODERATE
        if 'risk factor' in explanation_lower:
            return RECOMMENDATION_MAP["MODERATE"]
        else:
            return RECOMMENDATION_MAP["LOW"]


def _generate_explanation(rag_answer: str, detected_risks: List[str], overall_risk: str) -> str:
    """
    Extract comprehensive clinical explanation from RAG answer.
    
    Args:
        rag_answer: Full RAG-generated answer
        detected_risks: List of detected risk conditions
        overall_risk: Overall risk level
        
    Returns:
        Comprehensive clinical explanation
    """
    # Extract the clinical assessment from RAG answer
    # Skip disclaimer and extract the main clinical content
    
    lines = rag_answer.split('\n')
    explanation_parts = []
    skip_patterns = ['CLINICAL DECISION SUPPORT', 'NOT A DIAGNOSIS', 'disclaimer', 'AI-powered', 'must be verified', '===', '---', '***']
    
    in_risk_section = False
    in_evidence_section = False
    in_recommendation_section = False
    
    for line in lines:
        line_stripped = line.strip()
        line_lower = line_stripped.lower()
        
        # Skip disclaimer and formatting
        if any(pattern.lower() in line_lower for pattern in skip_patterns):
            continue
        
        # Skip markdown headers
        if line_stripped.startswith('#'):
            # But capture section markers
            if 'risk' in line_lower:
                in_risk_section = True
                in_evidence_section = False
                in_recommendation_section = False
            elif 'evidence' in line_lower:
                in_risk_section = False
                in_evidence_section = True
                in_recommendation_section = False
            elif 'recommendation' in line_lower or 'management' in line_lower:
                in_risk_section = False
                in_evidence_section = False
                in_recommendation_section = True
            continue
        
        # Skip empty lines
        if not line_stripped:
            continue
        
        # Collect relevant content
        if in_risk_section or in_evidence_section:
            explanation_parts.append(line_stripped)
    
    # If we got good content from RAG, use it
    if explanation_parts and len(' '.join(explanation_parts)) > 100:
        explanation = ' '.join(explanation_parts)
        
        # Add risk level statement if not present
        if overall_risk not in explanation:
            explanation = f"Risk Assessment: {overall_risk}. {explanation}"
    else:
        # Fallback: Generate from detected risks
        if not detected_risks:
            explanation = f"Risk Assessment: {overall_risk}. No significant risk factors detected. Patient has normal vital signs and laboratory values within acceptable range for gestational age."
        else:
            risk_list = ', '.join(detected_risks)
            explanation = f"Risk Assessment: {overall_risk}. Patient presents with {len(detected_risks)} significant risk factor{'s' if len(detected_risks) > 1 else ''}: {risk_list}."
            
            if overall_risk == "CRITICAL":
                explanation += " CRITICAL risk level requires immediate specialist intervention."
            elif overall_risk == "HIGH":
                explanation += " HIGH risk level requires urgent obstetric consultation."
            elif overall_risk == "MODERATE":
                explanation += " MODERATE risk level requires enhanced antenatal care with specialist consultation."
    
    # Clean up
    explanation = explanation.replace('*', '').replace('#', '').strip()
    
    # Ensure it's not too long (max 800 chars for comprehensive explanation)
    if len(explanation) > 800:
        truncated = explanation[:797]
        last_period = truncated.rfind('.')
        if last_period > 600:
            explanation = explanation[:last_period + 1]
        else:
            explanation = truncated + "..."
    
    return explanation


def _build_clinical_query(data: StructuredData, summary: str) -> str:
    """
    Convert structured data to clinical query text.
    
    Args:
        data: Structured patient data
        summary: Clinical summary
        
    Returns:
        Clinical query string for RAG pipeline
    """
    patient = data.patient_info
    history = data.medical_history
    vitals = data.vitals
    labs = data.lab_reports
    pregnancy = data.pregnancy_details
    symptoms = data.current_symptoms
    
    # Build comprehensive clinical query
    query_parts = []
    
    # Patient demographics
    query_parts.append(f"A {patient.age}-year-old")
    if patient.gravida and patient.para:
        query_parts.append(f"G{patient.gravida}P{patient.para}")
    if patient.gestationalWeeks:
        query_parts.append(f"at {patient.gestationalWeeks} weeks")
    
    # Vitals
    query_parts.append(f"presents with BP {vitals.bpSystolic}/{vitals.bpDiastolic} mmHg")
    
    # Labs
    query_parts.append(f"and Hb {labs.hemoglobin} g/dL")
    if labs.fastingBloodSugar:
        query_parts.append(f", FBS {labs.fastingBloodSugar} mg/dL")
    if labs.urineProtein:
        query_parts.append(", proteinuria present")
    
    # Medical history
    history_items = []
    if history.previousLSCS:
        history_items.append("previous LSCS")
    if history.chronicHypertension:
        history_items.append("chronic hypertension")
    if history.diabetes:
        history_items.append("diabetes")
    if history.thyroidDisorder:
        history_items.append("thyroid disorder")
    if history.badObstetricHistory:
        history_items.append("bad obstetric history")
    
    if history_items:
        query_parts.append(f". History of {', '.join(history_items)}")
    else:
        query_parts.append(". No significant medical history")
    
    # Pregnancy details
    pregnancy_items = []
    if pregnancy.twinPregnancy:
        pregnancy_items.append("twin pregnancy")
    if pregnancy.placentaPrevia:
        pregnancy_items.append("placenta previa")
    if pregnancy.reducedFetalMovement:
        pregnancy_items.append("reduced fetal movements")
    if pregnancy.malpresentation:
        pregnancy_items.append("malpresentation")
    
    if pregnancy_items:
        query_parts.append(f". Current pregnancy: {', '.join(pregnancy_items)}")
    
    # Physical findings
    physical_items = []
    if vitals.pallor:
        physical_items.append("pallor")
    if vitals.pedalEdema:
        physical_items.append("pedal edema")
    
    if physical_items:
        query_parts.append(f". Physical examination shows {', '.join(physical_items)}")
    
    # Current symptoms
    symptom_items = []
    if symptoms.headache:
        symptom_items.append("headache")
    if symptoms.visualDisturbance:
        symptom_items.append("visual disturbances")
    if symptoms.epigastricPain:
        symptom_items.append("epigastric pain")
    if symptoms.decreasedUrineOutput:
        symptom_items.append("decreased urine output")
    if symptoms.bleedingPerVagina:
        symptom_items.append("bleeding per vagina")
    if symptoms.convulsions:
        symptom_items.append("convulsions")
    
    if symptom_items:
        query_parts.append(f". Complains of {', '.join(symptom_items)}")
    else:
        query_parts.append(". No acute symptoms")
    
    # Combine all parts
    clinical_query = " ".join(query_parts) + "."
    
    # Add summary if different from generated query
    if summary and summary.lower() not in clinical_query.lower():
        clinical_query = f"{summary}. {clinical_query}"
    
    return clinical_query


@app.get("/care-levels")
async def get_care_levels():
    """Get available care levels and their descriptions."""
    from config_production import CARE_LEVELS
    
    return {
        "care_levels": {
            level: {
                "name": info['name'],
                "allowed_actions": info['allowed_actions'],
                "forbidden_treatments": info['forbidden_treatments']
            }
            for level, info in CARE_LEVELS.items()
        }
    }


@app.get("/system-info")
async def get_system_info():
    """Get system information and capabilities."""
    return {
        "system": "Medical RAG - High-Risk Pregnancy Detection",
        "version": "1.0.0",
        "status": "production",
        "capabilities": {
            "feature_extraction": "Hybrid (Regex + LLM)",
            "retrieval": "FAISS + BM25 + RRF + Cross-encoder",
            "rule_engine": "12 clinical rules",
            "reasoning": "Evidence-grounded LLM",
            "hallucination_prevention": "Evidence attribution + Severity constraints",
            "confidence_scoring": "Weighted multi-component with ceilings",
            "care_level_awareness": "ASHA, PHC, CHC, District"
        },
        "clinical_rules": [
            "Advanced maternal age (≥35)",
            "Young maternal age (<20)",
            "Teenage pregnancy (<18)",
            "Severe anemia (Hb <7)",
            "Moderate anemia (Hb 7-10)",
            "Mild anemia (Hb 10-11)",
            "Severe hypertension (≥160/110)",
            "Hypertension (≥140/90)",
            "Overt diabetes (FBS ≥126)",
            "GDM (FBS ≥92)",
            "Twin pregnancy",
            "Previous cesarean",
            "Placenta previa"
        ],
        "safety_features": [
            "Evidence-gated validation (no hallucinations)",
            "Confidence ceilings (no overconfidence)",
            "Care-level filtering (appropriate recommendations)",
            "Severity constraint filters (no escalation)",
            "Topic isolation (condition-specific chunks)",
            "Drug completeness validation",
            "Steroid gating (appropriate timing)",
            "Internal consistency checks",
            "Citation validity",
            "Differential diagnosis clarity"
        ]
    }


# ============================================================
# Error Handlers
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )


# ============================================================
# Run Server
# ============================================================

if __name__ == "__main__":
    print("🏥 Medical RAG API Server")
    print("=" * 70)
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 70)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled for testing
        log_level="info"
    )
