# ============================================================
# enhanced_rag_pipeline.py — Integrated clinical RAG pipeline
# ============================================================
"""
PRODUCTION-READY HIGH-RISK PREGNANCY DETECTION RAG SYSTEM

Pipeline Flow:
1. Query Preprocessing → Extract clinical features, rewrite query
2. Clinical Risk Scoring → Rule-based risk assessment
3. Enhanced Retrieval → FAISS + MMR + clinical reranking
4. Controlled Generation → Confidence-based LLM prompts
5. Debug Mode → Full transparency for evaluation

Design Goals:
- High recall retrieval (catch all relevant risks)
- High precision (no false positives from lab value bias)
- Zero hallucinations (strict grounding)
- Clinical reasoning transparency
- Maintainable modular architecture
"""

import logging
from typing import Dict, Optional
from clinical_preprocessor import ClinicalPreprocessor
from clinical_risk_scorer import ClinicalRiskScorer
from enhanced_retriever import EnhancedRetriever
from controlled_generator import ControlledGenerator
from config import LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class EnhancedRAGPipeline:
    """
    Integrated RAG pipeline for clinical high-risk pregnancy detection.
    
    Features:
    - Structured clinical feature extraction
    - Evidence-based risk scoring
    - Feature-aware retrieval with clinical reranking
    - Controlled generation with confidence adaptation
    - Full debug mode for transparency
    """
    
    def __init__(self, index_dir: str = None):
        """Initialize all pipeline components."""
        print("[PIPELINE] Initializing enhanced RAG pipeline...")
        
        # Import config here to get default index directory
        from config import FAISS_INDEX_DIR
        if index_dir is None:
            index_dir = FAISS_INDEX_DIR
        
        self.preprocessor = ClinicalPreprocessor()
        self.risk_scorer = ClinicalRiskScorer()
        self.retriever = EnhancedRetriever(index_dir=index_dir)
        self.generator = ControlledGenerator()
        
        print("[PIPELINE] All components loaded successfully.")
    
    def run(self,
            query: str,
            top_k: int = 8,
            use_mmr: bool = True,
            debug: bool = False,
            verbose: bool = True) -> Dict:
        """
        Run full RAG pipeline with clinical awareness.
        
        Args:
            query: User query (free text)
            top_k: Number of chunks to retrieve
            use_mmr: Use Max Marginal Relevance for diversity
            debug: Return full debug information
            verbose: Print progress information
            
        Returns:
            Dict with answer, risk assessment, and optional debug info
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"QUERY: {query}")
            print(f"{'='*70}")
        
        # ============================================================
        # LAYER 1: Query Preprocessing
        # ============================================================
        if verbose:
            print("\n[LAYER 1] Query Preprocessing...")
        
        preprocessing_result = self.preprocessor.process_query(query)
        features = preprocessing_result['extracted_features']
        rewritten_query = preprocessing_result['rewritten_query']
        
        if verbose:
            print(f"  Extracted features: Age={features.age}, BP={features.systolic_bp}/{features.diastolic_bp}, "
                  f"Hb={features.hemoglobin}")
            print(f"  Age risk: {features.age_risk_category}")
            print(f"  Anemia risk: {features.anemia_risk}")
            print(f"  BP risk: {features.bp_risk}")
            if rewritten_query != query:
                print(f"  Query rewritten: {rewritten_query[:100]}...")
        
        # ============================================================
        # LAYER 2: Clinical Risk Scoring
        # ============================================================
        if verbose:
            print("\n[LAYER 2] Clinical Risk Scoring...")
        
        risk_assessment = self.risk_scorer.score_risk(features)
        
        if verbose:
            print(f"  Risk Level: {risk_assessment.risk_level.upper()}")
            print(f"  Risk Score: {risk_assessment.total_score}")
            print(f"  Risk Factors: {len(risk_assessment.risk_factors)}")
            for rf in risk_assessment.risk_factors:
                print(f"    • {rf['factor']}: {rf['value']} (Score: {rf['score']})")
        
        # ============================================================
        # LAYER 3: Enhanced Retrieval
        # ============================================================
        if verbose:
            print("\n[LAYER 3] Enhanced Retrieval...")
        
        retrieval_result = self.retriever.retrieve(
            query=query,
            rewritten_query=rewritten_query,
            features=features,
            top_k=top_k,
            use_mmr=use_mmr,
            verbose=verbose
        )
        
        chunks = retrieval_result['chunks']
        confidence = retrieval_result['confidence']
        metadata = retrieval_result['metadata']
        
        # Format context for LLM
        context = self.retriever.format_context(chunks) if chunks else None
        
        # ============================================================
        # LAYER 4: Controlled Generation
        # ============================================================
        if verbose:
            print("\n[LAYER 4] Controlled Generation...")
        
        if context:
            generation_result = self.generator.generate(
                query=query,
                context=context,
                confidence=confidence,
                risk_assessment=risk_assessment,
                verbose=verbose
            )
            answer = generation_result['answer']
        else:
            # No context retrieved - use fallback
            answer = self.generator.generate_no_context_response(query)
            confidence = "none"
        
        # ============================================================
        # LAYER 5: Result Assembly
        # ============================================================
        result = {
            'query': query,
            'answer': answer,
            'confidence': confidence,
            'risk_assessment': risk_assessment.to_dict(),
            'metadata': metadata,
            'stats': retrieval_result['stats'],
        }
        
        # Add debug information if requested
        if debug:
            result['debug'] = {
                'extracted_features': preprocessing_result['feature_dict'],
                'rewritten_query': rewritten_query,
                'retrieved_chunks': [
                    {
                        'rank': i + 1,
                        'content': doc.page_content[:200] + "...",
                        'page': doc.metadata.get('page_number'),
                        'section': doc.metadata.get('section_name'),
                        'rerank_score': float(score),
                    }
                    for i, (doc, _, score) in enumerate(chunks)
                ],
                'risk_factors_detail': risk_assessment.risk_factors,
                'recommendations': risk_assessment.recommendations,
            }
        
        # Log result
        logging.info(
            f"RAG_COMPLETE | query='{query[:50]}...' | "
            f"confidence={confidence} | risk_level={risk_assessment.risk_level} | "
            f"risk_score={risk_assessment.total_score} | "
            f"chunks_retrieved={len(chunks)} | "
            f"pages={metadata.get('pages', [])}"
        )
        
        if verbose:
            print(f"\n{'='*70}")
            print("PIPELINE COMPLETE")
            print(f"{'='*70}")
        
        return result
    
    def format_result(self, result: Dict, include_debug: bool = False) -> str:
        """Format result as human-readable text."""
        lines = []
        
        lines.append("="*70)
        lines.append(f"QUERY: {result['query']}")
        lines.append("="*70)
        
        # Risk Assessment
        risk = result['risk_assessment']
        lines.append(f"\nRISK ASSESSMENT:")
        lines.append(f"  Level: {risk['risk_level'].upper()}")
        lines.append(f"  Score: {risk['total_score']}")
        
        if risk['risk_factors']:
            lines.append(f"\n  Risk Factors:")
            for rf in risk['risk_factors']:
                lines.append(f"    • {rf['factor']}: {rf['value']} (Score: {rf['score']}, Severity: {rf['severity']})")
        
        # Retrieval Stats
        stats = result['stats']
        lines.append(f"\nRETRIEVAL STATS:")
        lines.append(f"  Confidence: {result['confidence'].upper()}")
        lines.append(f"  Chunks Retrieved: {stats['final_count']}")
        lines.append(f"  Top Rerank Score: {stats['top_rerank_score']:.3f}")
        lines.append(f"  Pages Used: {result['metadata']['pages']}")
        
        # Answer
        lines.append(f"\nANSWER:")
        lines.append("-"*70)
        lines.append(result['answer'])
        lines.append("-"*70)
        
        # Debug info
        if include_debug and 'debug' in result:
            debug = result['debug']
            lines.append(f"\nDEBUG INFORMATION:")
            lines.append(f"\nExtracted Features:")
            for key, value in debug['extracted_features'].items():
                if value is not None and value != False:
                    lines.append(f"  {key}: {value}")
            
            lines.append(f"\nRewritten Query:")
            lines.append(f"  {debug['rewritten_query'][:200]}...")
            
            lines.append(f"\nRetrieved Chunks:")
            for chunk in debug['retrieved_chunks']:
                lines.append(f"  [{chunk['rank']}] Page {chunk['page']} | Score: {chunk['rerank_score']:.3f}")
                lines.append(f"      {chunk['content']}")
        
        lines.append("="*70)
        
        return "\n".join(lines)


# ============================================================
# Convenience function for backward compatibility
# ============================================================
def run_rag(query: str, 
            top_k: int = 8,
            debug: bool = False,
            verbose: bool = True) -> Dict:
    """
    Convenience function to run enhanced RAG pipeline.
    Maintains backward compatibility with existing code.
    
    Args:
        query: User query
        top_k: Number of chunks to retrieve
        debug: Return debug information
        verbose: Print progress
        
    Returns:
        Result dictionary
    """
    pipeline = EnhancedRAGPipeline()
    return pipeline.run(query, top_k=top_k, debug=debug, verbose=verbose)


# ============================================================
# Example usage
# ============================================================
if __name__ == "__main__":
    # Example queries demonstrating the system
    test_queries = [
        "38-year-old pregnant woman with BP 150/95 and Hb 10.5",
        "Is a 25-year-old with normal vitals at risk?",
        "Twin pregnancy with previous cesarean section",
        "What is the prevalence of high-risk pregnancy in India?",
    ]
    
    pipeline = EnhancedRAGPipeline()
    
    for query in test_queries:
        result = pipeline.run(query, debug=True, verbose=True)
        print(pipeline.format_result(result, include_debug=True))
        print("\n" * 2)
