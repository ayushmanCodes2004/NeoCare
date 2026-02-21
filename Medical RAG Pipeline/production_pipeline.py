# ============================================================
# production_pipeline.py — Integrated Production RAG Pipeline
# ============================================================
"""
PRODUCTION RAG PIPELINE

4-Layer Architecture:
1. Clinical Feature Extraction (Deterministic)
2. Hybrid Retrieval (FAISS + BM25 + Reranking)
3. Clinical Rule Engine (Authoritative)
4. Evidence-Grounded Reasoning (LLM)

With:
- Weighted confidence scoring
- Hallucination guards
- Debug telemetry
"""

import logging
from typing import Dict
from layer1_extractor import ClinicalFeatureExtractor
from layer2_retrieval import HybridRetriever
# from layer3_rules import ClinicalRuleEngine  # REMOVED: Using clinical_rules.py instead
from layer4_reasoning import EvidenceGroundedReasoner
from confidence_scorer import calculate_confidence
from hallucination_guard import check_hallucination_risk, format_blocked_response
from config_production import LOG_FILE, DEBUG_MODE
from clinical_rules import run_rule_engine, RuleEngineResult  # NEW: Pre-RAG rule engine only

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class ProductionRAGPipeline:
    """
    Production-grade medical RAG pipeline.
    
    Features:
    - Deterministic feature extraction
    - Hybrid retrieval (FAISS + BM25)
    - Authoritative rule engine
    - Evidence-grounded LLM
    - Hallucination prevention
    - Full debug telemetry
    """
    
    def __init__(self, index_dir: str = None):
        """Initialize all pipeline components."""
        print("\n" + "="*70)
        print("PRODUCTION MEDICAL RAG PIPELINE")
        print("="*70)
        print("\nInitializing components...")
        
        # Layer 1: Feature Extractor
        print("[1/4] Loading Clinical Feature Extractor...")
        self.extractor = ClinicalFeatureExtractor()
        
        # Layer 2: Hybrid Retriever
        print("[2/4] Loading Hybrid Retriever...")
        self.retriever = HybridRetriever(index_dir=index_dir)
        
        # Layer 3: Rule Engine (using clinical_rules.py pre-RAG engine)
        print("[3/4] Clinical Rule Engine ready (pre-RAG)...")
        # No initialization needed - using run_rule_engine() function
        
        # Layer 4: Reasoner
        print("[4/4] Loading Evidence-Grounded Reasoner...")
        self.reasoner = EvidenceGroundedReasoner()
        
        print("\n[OK] All components loaded successfully")
        print("="*70)
    
    def run(self, query: str, verbose: bool = True, care_level: str = None, input_type: str = "text") -> Dict:
        """
        Run full production RAG pipeline with safety features.
        
        Args:
            query: User query (free text)
            verbose: Print debug telemetry
            care_level: Care level context ('ASHA', 'PHC', 'CHC', 'DISTRICT')
            input_type: "text" or "structured_json" (for confidence calculation)
            
        Returns:
            Complete result dict with answer, confidence, and debug info
        """
        from config_production import DEFAULT_CARE_LEVEL
        
        if care_level is None:
            care_level = DEFAULT_CARE_LEVEL
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"QUERY: {query}")
            print(f"CARE LEVEL: {care_level}")
            print(f"{'='*70}")
        
        # ============================================================
        # LAYER 1: Clinical Feature Extraction
        # ============================================================
        if verbose:
            print("\n[LAYER 1] Clinical Feature Extraction")
            print("-" * 70)
        
        features = self.extractor.extract(query, verbose=verbose)
        
        if verbose:
            print(f"\nExtracted Features:")
            if features.age:
                print(f"  Age: {features.age} years")
            if features.gestational_age_weeks:
                print(f"  Gestational Age: {features.gestational_age_weeks} weeks")
            if features.systolic_bp:
                print(f"  BP: {features.systolic_bp}/{features.diastolic_bp} mmHg")
            if features.hemoglobin:
                print(f"  Hb: {features.hemoglobin} g/dL")
            if features.fbs:
                print(f"  FBS: {features.fbs} mg/dL")
            if features.twin_pregnancy:
                print(f"  Twin Pregnancy: Yes")
            if features.prior_cesarean:
                print(f"  Previous Cesarean: Yes")
            if features.placenta_previa:
                print(f"  Placenta Previa: Yes")
            print(f"\nExtraction Confidence: {features.extraction_confidence:.2f}")
            if features.missing_fields:
                print(f"Missing Fields: {', '.join(features.missing_fields)}")
        
        # ============================================================
        # PRE-RETRIEVAL: Clinical Rule Engine (Hard-coded Thresholds)
        # ============================================================
        if verbose:
            print(f"\n[PRE-RETRIEVAL] Clinical Rule Engine")
            print("-" * 70)
        
        # Convert features to dict for rule engine
        features_dict = {
            'age': features.age,
            'gestational_age_weeks': features.gestational_age_weeks,
            'systolic_bp': features.systolic_bp,
            'diastolic_bp': features.diastolic_bp,
            'hemoglobin': features.hemoglobin,
            'fbs': features.fbs,
            'ogtt_2hr_pg': features.ogtt,
            'proteinuria': features.proteinuria if hasattr(features, 'proteinuria') else False,
            'seizures': features.seizures if hasattr(features, 'seizures') else False,
            'twin_pregnancy': features.twin_pregnancy,
            'prior_cesarean': features.prior_cesarean,
            'placenta_previa': features.placenta_previa,
        }
        
        # Run pre-RAG rule engine
        pre_rag_rules = run_rule_engine(features_dict, verbose=verbose)
        
        if verbose:
            print(f"\n[PRE-RAG RULES] Confirmed Conditions: {pre_rag_rules.confirmed_conditions}")
            print(f"[PRE-RAG RULES] Suspected Conditions: {pre_rag_rules.suspected_conditions}")
            print(f"[PRE-RAG RULES] Risk Score: {pre_rag_rules.risk_score}")
            print(f"[PRE-RAG RULES] Risk Level: {pre_rag_rules.risk_level}")
            print(f"[PRE-RAG RULES] Referral: {pre_rag_rules.referral_facility}")
        
        # ============================================================
        # LAYER 2: Hybrid Retrieval
        # ============================================================
        if verbose:
            print(f"\n[LAYER 2] Hybrid Retrieval")
            print("-" * 70)
        
        retrieval_result = self.retriever.retrieve(
            query, features, verbose=verbose
        )
        
        # ============================================================
        # EVIDENCE VALIDATION: Remove hallucinated features
        # ============================================================
        if verbose:
            print(f"\n[EVIDENCE VALIDATION] Checking for hallucinations...")
        
        # Get retrieved chunks for validation
        retrieved_chunks = [doc for doc, _ in retrieval_result.get('chunks', [])]
        
        # Validate features against evidence
        features = self.extractor.validate_against_evidence(
            features, query, retrieved_chunks
        )
        
        if verbose:
            print(f"[EVIDENCE VALIDATION] Features validated against query + evidence")
        
        # ============================================================
        # USE PRE-RAG RULES AS AUTHORITATIVE (No Layer 3 merge)
        # ============================================================
        # Convert pre_rag_rules to expected format
        rule_output = pre_rag_rules  # RuleEngineResult already has all needed fields
        
        if verbose:
            print(f"\n[RULE ENGINE] Clinical Rules Applied")
            print("-" * 70)
            print(f"  Overall Risk: {rule_output.risk_level}")
            print(f"  Total Score: {rule_output.risk_score}")
            print(f"  Rule Coverage: {rule_output.rule_coverage:.2f}")
            print(f"  Triggered Rules: {', '.join(rule_output.triggered_rules)}")
            if rule_output.risk_flags:
                print(f"\n  Risk Flags:")
                for flag in rule_output.risk_flags:
                    print(f"    • {flag['condition']}: {flag['value']} (Severity: {flag['severity']})")
        
        # ============================================================
        # CONFIDENCE SCORING
        # ============================================================
        if verbose:
            print(f"\n[CONFIDENCE SCORING]")
            print("-" * 70)
        
        confidence = calculate_confidence(
            retrieval_quality=retrieval_result['retrieval_quality'],
            rule_coverage=rule_output.rule_coverage,
            chunk_agreement=retrieval_result['chunk_agreement'],
            extractor_confidence=features.extraction_confidence,
            input_type=input_type,  # FIX 2: Pass input_type for structured JSON boost
            verbose=verbose
        )
        
        # ============================================================
        # HALLUCINATION GUARD
        # ============================================================
        if verbose:
            print(f"\n[HALLUCINATION GUARD]")
            print("-" * 70)
        
        guard_result = check_hallucination_risk(
            confidence_score=confidence['score'],
            retrieval_quality=retrieval_result['retrieval_quality'],
            verbose=verbose
        )
        
        if not guard_result['allow_output']:
            answer = format_blocked_response(guard_result)
            
            result = {
                'query': query,
                'answer': answer,
                'blocked': True,
                'guard_result': guard_result,
                'confidence': confidence,
                'features': self.extractor.to_dict(features),
                'rule_output': {
                    'overall_risk': rule_output.risk_level,
                    'total_score': rule_output.risk_score,
                    'rule_coverage': rule_output.rule_coverage,
                    'risk_flags': [
                        {
                            'condition': f.get('condition', ''),
                            'present': f.get('present', False),
                            'value': f.get('value', ''),
                            'severity': f.get('severity', ''),
                        }
                        for f in rule_output.risk_flags
                    ]
                },
                'retrieval_stats': {
                    'faiss_count': retrieval_result['faiss_count'],
                    'bm25_count': retrieval_result['bm25_count'],
                    'final_count': retrieval_result['final_count'],
                    'retrieval_quality': retrieval_result['retrieval_quality'],
                    'chunk_agreement': retrieval_result['chunk_agreement'],
                }
            }
            
            if verbose:
                print(f"\n{'='*70}")
                print("PIPELINE BLOCKED BY HALLUCINATION GUARD")
                print(f"{'='*70}")
            
            # Log
            logging.warning(
                f"BLOCKED | query='{query[:50]}...' | "
                f"confidence={confidence['score']:.2f} | "
                f"retrieval_quality={retrieval_result['retrieval_quality']:.2f}"
            )
            
            return result
        
        # ============================================================
        # LAYER 4: Evidence-Grounded Reasoning
        # ============================================================
        if verbose:
            print(f"\n[LAYER 4] Evidence-Grounded Reasoning")
            print("-" * 70)
        
        answer = self.reasoner.generate_response(
            query=query,
            features=features,
            rule_output=rule_output,
            retrieval_result=retrieval_result,
            confidence=confidence,
            care_level=care_level,  # Pass care level
            verbose=verbose
        )
        
        # ============================================================
        # FINAL RESULT
        # ============================================================
        result = {
            'query': query,
            'answer': answer,
            'blocked': False,
            'confidence': confidence,
            'features': self.extractor.to_dict(features),
            'rule_output': {
                'overall_risk': rule_output.risk_level,
                'total_score': rule_output.risk_score,
                'rule_coverage': rule_output.rule_coverage,
                'triggered_rules': rule_output.triggered_rules,
                'risk_flags': [
                    {
                        'condition': f.get('condition', ''),
                        'present': f.get('present', False),
                        'value': f.get('value', ''),
                        'threshold': f.get('threshold', 'N/A'),
                        'severity': f.get('severity', ''),
                        'rationale': f.get('rationale', ''),
                        'score': f.get('score', 0),
                    }
                    for f in rule_output.risk_flags
                ]
            },
            'retrieval_stats': {
                'rewritten_query': retrieval_result['rewritten_query'],
                'faiss_count': retrieval_result['faiss_count'],
                'bm25_count': retrieval_result['bm25_count'],
                'final_count': retrieval_result['final_count'],
                'retrieval_quality': retrieval_result['retrieval_quality'],
                'chunk_agreement': retrieval_result['chunk_agreement'],
            }
        }
        
        # Log success
        logging.info(
            f"SUCCESS | query='{query[:50]}...' | "
            f"confidence={confidence['score']:.2f} ({confidence['level']}) | "
            f"risk={rule_output.risk_level} | "
            f"score={rule_output.risk_score}"
        )
        
        if verbose:
            print(f"\n{'='*70}")
            print("PIPELINE COMPLETE")
            print(f"{'='*70}")
        
        return result
    
    def print_result(self, result: Dict):
        """Pretty-print pipeline result."""
        print("\n" + "="*70)
        print("PRODUCTION RAG RESULT")
        print("="*70)
        
        if result['blocked']:
            print("\n⚠️ OUTPUT BLOCKED BY HALLUCINATION GUARD")
            print(f"Reason: {result['guard_result']['reason']}")
            print("\nDetails:")
            for reason in result['guard_result']['detailed_reasons']:
                print(f"  • {reason}")
        else:
            print("\n" + result['answer'])
        
        print("\n" + "="*70)


# ============================================================
# Convenience function
# ============================================================
def run_production_rag(query: str, verbose: bool = True) -> Dict:
    """
    Convenience function to run production RAG.
    
    Args:
        query: User query
        verbose: Print debug telemetry
        
    Returns:
        Result dict
    """
    pipeline = ProductionRAGPipeline()
    return pipeline.run(query, verbose=verbose)


# ============================================================
# Example usage
# ============================================================
if __name__ == "__main__":
    # Test query
    test_query = "38-year-old pregnant woman with BP 150/95, Hb 10.5, twin pregnancy"
    
    pipeline = ProductionRAGPipeline()
    result = pipeline.run(test_query, verbose=True)
    pipeline.print_result(result)
