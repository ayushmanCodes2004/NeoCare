# ============================================================
# final_rag_pipeline.py — Production-ready RAG with all improvements
# ============================================================
"""
FINAL PRODUCTION RAG PIPELINE

All improvements implemented:
✅ FAISS scoring fix (distance → similarity)
✅ Metadata-aware retrieval with topic boosting
✅ Hybrid search (FAISS + BM25 + RRF)
✅ Cross-encoder reranking
✅ Document coverage detection (5 tiers)
✅ Clinical rule engine
✅ Structured query rewriting
✅ Confidence scoring with breakdown
✅ Coverage-aware generation
✅ No generic fallbacks
✅ Debug mode
"""

import logging
from typing import Dict
from clinical_preprocessor import ClinicalPreprocessor
from clinical_risk_scorer import ClinicalRiskScorer
from improved_retriever import ImprovedRetriever
from improved_generator import ImprovedGenerator
from config import LOG_FILE

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class FinalRAGPipeline:
    """
    Production-ready RAG pipeline with comprehensive improvements.
    """
    
    def __init__(self, index_dir: str = None):
        """Initialize all pipeline components."""
        print("[PIPELINE] Initializing final production RAG pipeline...")
        
        from config import FAISS_INDEX_DIR
        if index_dir is None:
            index_dir = FAISS_INDEX_DIR
        
        self.preprocessor = ClinicalPreprocessor()
        self.risk_scorer = ClinicalRiskScorer()
        self.retriever = ImprovedRetriever(index_dir=index_dir)
        self.generator = ImprovedGenerator()
        
        print("[PIPELINE] All components loaded successfully.")
        print("[PIPELINE] Features enabled:")
        print("  ✅ FAISS distance→similarity conversion")
        print("  ✅ Hybrid search (FAISS + BM25 + RRF)")
        print("  ✅ Metadata-aware topic boosting")
        print("  ✅ Cross-encoder reranking")
        print("  ✅ Document coverage detection")
        print("  ✅ Clinical rule engine")
        print("  ✅ Confidence breakdown")
    
    def run(self,
            query: str,
            top_k: int = 8,
            debug: bool = False,
            verbose: bool = True) -> Dict:
        """
        Run full production RAG pipeline.
        
        Args:
            query: User query
            top_k: Number of chunks to retrieve
            debug: Return full debug information
            verbose: Print progress
            
        Returns:
            Complete result dict
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"QUERY: {query}")
            print(f"{'='*70}")
        
        # ============================================================
        # LAYER 1: Query Preprocessing & Feature Extraction
        # ============================================================
        if verbose:
            print("\n[LAYER 1] Query Preprocessing & Feature Extraction...")
        
        preprocessing_result = self.preprocessor.process_query(query)
        features = preprocessing_result['extracted_features']
        rewritten_query = preprocessing_result['rewritten_query']
        
        if verbose:
            print(f"  Extracted features:")
            if features.age:
                print(f"    Age: {features.age} years ({features.age_risk_category})")
            if features.systolic_bp:
                print(f"    BP: {features.systolic_bp}/{features.diastolic_bp} mmHg ({features.bp_risk})")
            if features.hemoglobin:
                print(f"    Hb: {features.hemoglobin} g/dL ({features.anemia_risk})")
            if features.fasting_glucose:
                print(f"    FBS: {features.fasting_glucose} mg/dL ({features.glucose_risk})")
            if features.gestational_age_weeks:
                print(f"    Gestational age: {features.gestational_age_weeks} weeks")
            
            print(f"\n  Structured query:")
            print(f"    {rewritten_query[:150]}...")
        
        # ============================================================
        # LAYER 2: Clinical Risk Scoring (Rule-Based)
        # ============================================================
        if verbose:
            print("\n[LAYER 2] Clinical Risk Scoring...")
        
        risk_assessment = self.risk_scorer.score_risk(features)
        
        if verbose:
            print(f"  Risk Level: {risk_assessment.risk_level.upper()}")
            print(f"  Risk Score: {risk_assessment.total_score}")
            if risk_assessment.risk_factors:
                print(f"  Risk Factors:")
                for rf in risk_assessment.risk_factors:
                    print(f"    • {rf['factor']}: {rf['value']} (Score: {rf['score']}, Severity: {rf['severity']})")
        
        # ============================================================
        # LAYER 3: Improved Retrieval (Hybrid + Reranking)
        # ============================================================
        if verbose:
            print("\n[LAYER 3] Improved Retrieval...")
        
        retrieval_result = self.retriever.retrieve(
            query=query,
            rewritten_query=rewritten_query,
            features=features,
            top_k=top_k,
            verbose=verbose
        )
        
        chunks = retrieval_result['chunks']
        confidence = retrieval_result['confidence']
        confidence_score = retrieval_result['confidence_score']
        confidence_breakdown = retrieval_result['confidence_breakdown']
        coverage = retrieval_result['coverage']
        topics = retrieval_result['topics']
        metadata = retrieval_result['metadata']
        
        # Format context
        context = self.retriever.format_context(chunks) if chunks else None
        
        # ============================================================
        # LAYER 4: Coverage-Aware Generation
        # ============================================================
        if verbose:
            print("\n[LAYER 4] Coverage-Aware Generation...")
        
        if context or coverage['derivable']:
            generation_result = self.generator.generate(
                query=query,
                context=context,
                features=features,
                risk_assessment=risk_assessment,
                coverage=coverage,
                confidence_breakdown=confidence_breakdown,
                verbose=verbose
            )
            answer = generation_result['answer']
            prompt_type = generation_result['prompt_type']
        else:
            # No context and not derivable
            answer = self._generate_no_coverage_response(query, coverage)
            prompt_type = "no_coverage"
        
        # ============================================================
        # LAYER 5: Result Assembly
        # ============================================================
        result = {
            'query': query,
            'answer': answer,
            'confidence': confidence,
            'confidence_score': confidence_score,
            'confidence_breakdown': confidence_breakdown,
            'coverage': coverage,
            'risk_assessment': risk_assessment.to_dict(),
            'metadata': metadata,
            'topics': topics,
            'stats': retrieval_result['stats'],
            'prompt_type': prompt_type,
        }
        
        # Add debug information
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
                        'similarity': float(sim_score),
                        'rerank_score': float(rerank_score),
                    }
                    for i, (doc, sim_score, rerank_score) in enumerate(chunks)
                ],
                'risk_factors_detail': risk_assessment.risk_factors,
                'recommendations': risk_assessment.recommendations,
                'coverage_detail': coverage,
            }
        
        # Log result
        logging.info(
            f"RAG_COMPLETE | query='{query[:50]}...' | "
            f"confidence={confidence} ({confidence_score:.2f}) | "
            f"coverage={coverage['tier']} | derivable={coverage['derivable']} | "
            f"risk_level={risk_assessment.risk_level} | risk_score={risk_assessment.total_score} | "
            f"chunks={len(chunks)} | pages={metadata.get('pages', [])}"
        )
        
        if verbose:
            print(f"\n{'='*70}")
            print("PIPELINE COMPLETE")
            print(f"{'='*70}")
        
        return result
    
    def _generate_no_coverage_response(self, query: str, coverage: Dict) -> str:
        """Generate response when no coverage is available."""
        response = f"""I could not find relevant information in the clinical document to answer: "{query}"

The document primarily covers:
- High-risk pregnancy prevalence in India (NFHS-5 data)
- Clinical management guidelines for: hypertension/eclampsia, anaemia, GDM, hypothyroidism, syphilis, IUGR, previous caesarean, placenta previa, twin pregnancy
- Government health schemes: PMSMA, JSY, JSSK, PMMMVY, DAKSHATA
- Clinical procedure charts: ANC, postnatal care, PPH, AMTSL, eclampsia management, neonatal resuscitation

You might want to ask about:
- Prevalence and risk factors for high-risk pregnancy
- Management of specific conditions (hypertension, anemia, diabetes in pregnancy)
- Clinical thresholds and diagnostic criteria
- Government maternal health schemes

❌ [NO COVERAGE — Question not addressed in document]"""
        return response
    
    def format_result(self, result: Dict, include_debug: bool = False) -> str:
        """Format result as human-readable text."""
        lines = []
        
        lines.append("="*70)
        lines.append(f"QUERY: {result['query']}")
        lines.append("="*70)
        
        # Clinical Rule Application
        lines.append(f"\nCLINICAL RULE APPLICATION:")
        if 'debug' in result and result['debug']['extracted_features']:
            features = result['debug']['extracted_features']
            if features.get('age'):
                age_cat = features.get('age_risk_category', 'normal_age')
                lines.append(f"  Age: {features['age']} years → {age_cat.replace('_', ' ').title()}")
            if features.get('hemoglobin'):
                hb_risk = features.get('anemia_risk', 'normal')
                lines.append(f"  Hb: {features['hemoglobin']} g/dL → {hb_risk.replace('_', ' ').title()}")
            if features.get('systolic_bp'):
                bp_risk = features.get('bp_risk', 'normal')
                lines.append(f"  BP: {features['systolic_bp']}/{features['diastolic_bp']} mmHg → {bp_risk.replace('_', ' ').title()}")
            if features.get('fasting_glucose'):
                glucose_risk = features.get('glucose_risk', 'normal')
                lines.append(f"  FBS: {features['fasting_glucose']} mg/dL → {glucose_risk.replace('_', ' ').title()}")
        
        # Risk Assessment
        risk = result['risk_assessment']
        lines.append(f"\nRISK ASSESSMENT:")
        lines.append(f"  Level: {risk['risk_level'].upper()}")
        lines.append(f"  Score: {risk['total_score']}")
        
        if risk['risk_factors']:
            lines.append(f"  Risk Factors:")
            for rf in risk['risk_factors']:
                lines.append(f"    • {rf['factor']}: {rf['value']} (Score: {rf['score']}, Severity: {rf['severity']})")
        else:
            lines.append(f"  No significant risk factors identified")
        
        # Document Coverage
        coverage = result['coverage']
        lines.append(f"\nDOCUMENT COVERAGE:")
        lines.append(f"  Tier: {coverage['tier'].upper()}")
        lines.append(f"  Derivable from Rules: {'YES' if coverage['derivable'] else 'NO'}")
        lines.append(f"  Has Clinical Rules: {'YES' if coverage['has_rules'] else 'NO'}")
        lines.append(f"  Covered Topics: {', '.join(coverage['covered_topics']) if coverage['covered_topics'] else 'None'}")
        
        # Confidence Breakdown
        lines.append(f"\nCONFIDENCE BREAKDOWN:")
        lines.append(f"  Overall: {result['confidence'].upper()} ({result['confidence_score']:.2f})")
        breakdown = result['confidence_breakdown']
        lines.append(f"  - Retrieval Quality: {breakdown['retrieval_quality']:.2f} (40% weight)")
        lines.append(f"  - Rule Coverage: {breakdown['rule_coverage']:.2f} (30% weight)")
        lines.append(f"  - Chunk Agreement: {breakdown['chunk_agreement']:.2f} (30% weight)")
        
        # Retrieval Stats
        stats = result['stats']
        lines.append(f"\nRETRIEVAL STATS:")
        lines.append(f"  FAISS: {stats['faiss_count']} chunks (top similarity: {stats['top_similarity']:.3f})")
        lines.append(f"  BM25: {stats['bm25_count']} chunks")
        lines.append(f"  Merged (RRF): {stats['merged_count']} chunks")
        lines.append(f"  Final (reranked): {stats['final_count']} chunks")
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
            
            lines.append(f"\nRewritten Query:")
            lines.append(f"  {debug['rewritten_query'][:200]}...")
            
            lines.append(f"\nRetrieved Chunks:")
            for chunk in debug['retrieved_chunks'][:5]:  # Show top 5
                lines.append(f"  [{chunk['rank']}] Page {chunk['page']} | Sim: {chunk['similarity']:.3f} | Rerank: {chunk['rerank_score']:.3f}")
                lines.append(f"      {chunk['content']}")
            
            if debug['recommendations']:
                lines.append(f"\nClinical Recommendations:")
                for rec in debug['recommendations']:
                    lines.append(f"  • {rec}")
        
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
    Convenience function to run final RAG pipeline.
    
    Args:
        query: User query
        top_k: Number of chunks to retrieve
        debug: Return debug information
        verbose: Print progress
        
    Returns:
        Result dictionary
    """
    pipeline = FinalRAGPipeline()
    return pipeline.run(query, top_k=top_k, debug=debug, verbose=verbose)


# ============================================================
# Example usage
# ============================================================
if __name__ == "__main__":
    # Test with the problematic query
    test_query = "a 38-year-old pregnant woman at 10 weeks gestation with BP: 118/76 mmHg Hb: 11.5 g/dL FBS: 90 mg/dL and no prior medical history"
    
    pipeline = FinalRAGPipeline()
    result = pipeline.run(test_query, debug=True, verbose=True)
    print(pipeline.format_result(result, include_debug=True))
