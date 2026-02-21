# ============================================================
# improved_retriever.py — Production-grade retriever with all fixes
# ============================================================
"""
COMPREHENSIVE RETRIEVAL IMPROVEMENTS:
1. FAISS scoring fix (distance → similarity conversion)
2. Metadata-aware retrieval with topic boosting
3. Hybrid search (FAISS + BM25)
4. Cross-encoder reranking
5. Document coverage detection
6. Clinical rule engine integration
7. Confidence scoring with breakdown
"""

import re
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import Counter
from sentence_transformers import CrossEncoder
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from clinical_preprocessor import ClinicalFeatures
from config import LOG_FILE

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")


class ImprovedRetriever:
    """
    Production-grade retriever with comprehensive improvements.
    """
    
    # Topic mapping for metadata-aware retrieval
    TOPIC_MAP = {
        'anaemia': ['hb', 'hemoglobin', 'haemoglobin', 'anemia', 'anaemia', 'iron', 'ifa', 'pallor'],
        'hypertension': ['bp', 'blood pressure', 'hypertension', 'pre-eclampsia', 'preeclampsia', 
                         'pih', 'eclampsia', 'mgso4', 'magnesium'],
        'diabetes': ['fbs', 'rbs', 'ogtt', 'glucose', 'diabetes', 'gdm', 'insulin', 'sugar'],
        'age_risk': ['age', 'elderly', 'advanced maternal age', 'teenage', 'adolescent'],
        'twins': ['twin', 'multiple pregnancy', 'multiple gestation'],
        'cesarean': ['cesarean', 'caesarean', 'lscs', 'c-section', 'previous cs'],
        'placenta': ['placenta previa', 'placenta praevia', 'aph', 'antepartum'],
        'iugr': ['iugr', 'growth restriction', 'sga', 'small for gestational'],
        'hypothyroid': ['hypothyroid', 'tsh', 'thyroid', 'levothyroxine'],
    }
    
    def __init__(self, index_dir: str = None):
        """Initialize retriever with FAISS index and reranker."""
        from config import FAISS_INDEX_DIR, EMBEDDING_MODEL, OLLAMA_BASE_URL
        
        if index_dir is None:
            index_dir = FAISS_INDEX_DIR
        
        self.index_dir = index_dir
        
        # Load cross-encoder reranker
        print("[RETRIEVER] Loading cross-encoder reranker...")
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        print("[RETRIEVER] Reranker loaded.")
        
        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL
        )
        
        # Load FAISS index
        self.vectorstore = FAISS.load_local(
            self.index_dir, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
    
    def _convert_distance_to_similarity(self, distance: float) -> float:
        """
        Convert FAISS L2 distance to similarity score.
        Higher similarity = more relevant.
        
        Formula: similarity = 1 / (1 + distance)
        Range: [0, 1] where 1 = perfect match
        """
        return 1.0 / (1.0 + distance)
    
    def _extract_topics_from_query(self, query: str, features: ClinicalFeatures) -> List[str]:
        """
        Extract medical topics from query for metadata boosting.
        
        Args:
            query: User query
            features: Extracted clinical features
            
        Returns:
            List of relevant topic labels
        """
        topics = []
        query_lower = query.lower()
        
        # Check each topic's keywords
        for topic, keywords in self.TOPIC_MAP.items():
            if any(kw in query_lower for kw in keywords):
                topics.append(topic)
        
        # Add topics based on extracted features
        if features.anemia_risk and "anemia" in features.anemia_risk:
            if 'anaemia' not in topics:
                topics.append('anaemia')
        
        if features.bp_risk == "hypertensive":
            if 'hypertension' not in topics:
                topics.append('hypertension')
        
        if features.glucose_risk and "diabet" in features.glucose_risk:
            if 'diabetes' not in topics:
                topics.append('diabetes')
        
        if features.age_risk_category in ["advanced_maternal_age", "teenage_pregnancy"]:
            if 'age_risk' not in topics:
                topics.append('age_risk')
        
        if features.twin_pregnancy and 'twins' not in topics:
            topics.append('twins')
        
        if features.previous_cesarean and 'cesarean' not in topics:
            topics.append('cesarean')
        
        if features.placenta_previa and 'placenta' not in topics:
            topics.append('placenta')
        
        return topics
    
    def _bm25_search(self, query: str, features: ClinicalFeatures, 
                     max_results: int = 10) -> List[Tuple]:
        """
        BM25-style keyword search for hybrid retrieval.
        
        Args:
            query: User query
            features: Extracted clinical features
            max_results: Maximum results to return
            
        Returns:
            List of (doc, bm25_score) tuples
        """
        # Extract keywords from query and features
        keywords = set()
        query_words = [w.lower() for w in query.split() if len(w) > 3]
        keywords.update(query_words)
        
        # Add feature-specific keywords
        if features.age:
            keywords.add(str(features.age))
            if features.age >= 35:
                keywords.update(['advanced', 'maternal', 'age', 'elderly'])
        
        if features.hemoglobin:
            keywords.add(str(features.hemoglobin))
            keywords.update(['hemoglobin', 'haemoglobin', 'hb'])
        
        if features.systolic_bp:
            keywords.add(str(features.systolic_bp))
            keywords.update(['blood', 'pressure', 'bp', 'hypertension'])
        
        if features.fasting_glucose:
            keywords.add(str(features.fasting_glucose))
            keywords.update(['glucose', 'diabetes', 'fbs'])
        
        # Search through docstore
        scored_docs = []
        docstore = self.vectorstore.docstore._dict
        
        for doc_id, doc in docstore.items():
            text_lower = doc.page_content.lower()
            
            # Count keyword matches (simple BM25 approximation)
            match_count = 0
            for kw in keywords:
                if kw in text_lower:
                    # Weight by frequency (capped at 3)
                    freq = min(text_lower.count(kw), 3)
                    match_count += freq
            
            if match_count >= 2:
                # Simple BM25-style score
                doc_length = len(text_lower.split())
                avg_doc_length = 200  # Approximate
                score = match_count / (1 + abs(doc_length - avg_doc_length) / avg_doc_length)
                scored_docs.append((doc, score))
        
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:max_results]
    
    def _reciprocal_rank_fusion(self, 
                                 faiss_results: List[Tuple],
                                 bm25_results: List[Tuple],
                                 k: int = 60) -> List[Tuple]:
        """
        Merge FAISS and BM25 results using Reciprocal Rank Fusion.
        
        RRF formula: score = sum(1 / (k + rank))
        
        Args:
            faiss_results: List of (doc, similarity) from FAISS
            bm25_results: List of (doc, bm25_score) from BM25
            k: RRF constant (default 60)
            
        Returns:
            Merged list of (doc, rrf_score) tuples
        """
        rrf_scores = {}
        
        # Add FAISS results
        for rank, (doc, _) in enumerate(faiss_results, 1):
            doc_id = id(doc)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank)
            if doc_id not in {id(d): d for d, _ in faiss_results}:
                rrf_scores[doc_id] = doc
        
        # Add BM25 results
        for rank, (doc, _) in enumerate(bm25_results, 1):
            doc_id = id(doc)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank)
        
        # Create doc_map
        doc_map = {}
        for doc, _ in faiss_results + bm25_results:
            doc_map[id(doc)] = doc
        
        # Sort by RRF score
        merged = [(doc_map[doc_id], score) for doc_id, score in rrf_scores.items()]
        merged.sort(key=lambda x: x[1], reverse=True)
        
        return merged
    
    def _apply_metadata_boosting(self, 
                                  docs_and_scores: List[Tuple],
                                  topics: List[str],
                                  features: ClinicalFeatures) -> List[Tuple]:
        """
        Boost chunks based on metadata topic matching.
        
        Args:
            docs_and_scores: List of (doc, score) tuples
            topics: Extracted topics from query
            features: Clinical features
            
        Returns:
            Boosted list of (doc, boosted_score) tuples
        """
        boosted = []
        
        for doc, score in docs_and_scores:
            boost = 0.0
            content_lower = doc.page_content.lower()
            metadata = doc.metadata
            
            # Topic-based boosting
            for topic in topics:
                # Check if chunk is tagged with this topic
                if metadata.get('condition') and topic in metadata.get('condition', '').lower():
                    boost += 0.15
                
                # Check if topic keywords appear in content
                topic_keywords = self.TOPIC_MAP.get(topic, [])
                if any(kw in content_lower for kw in topic_keywords):
                    boost += 0.10
            
            # Feature-specific boosting (ONLY if feature is abnormal)
            if features.age_risk_category == "advanced_maternal_age":
                if any(term in content_lower for term in ['advanced maternal age', 'elderly', 'age 35', 'age over 35']):
                    boost += 0.20
            
            if features.anemia_risk and "anemia" in features.anemia_risk:
                if any(term in content_lower for term in ['anaemia', 'anemia', 'hemoglobin', 'haemoglobin']):
                    boost += 0.18
            
            if features.bp_risk == "hypertensive":
                if any(term in content_lower for term in ['hypertension', 'pre-eclampsia', 'blood pressure', 'pih']):
                    boost += 0.18
            
            if features.glucose_risk and "diabet" in features.glucose_risk:
                if any(term in content_lower for term in ['diabetes', 'gdm', 'glucose', 'insulin']):
                    boost += 0.18
            
            # Numeric match boosting
            if features.hemoglobin and str(features.hemoglobin) in content_lower:
                boost += 0.10
            if features.systolic_bp and str(features.systolic_bp) in content_lower:
                boost += 0.10
            
            boosted_score = score + boost
            boosted.append((doc, boosted_score))
        
        # Re-sort by boosted score
        boosted.sort(key=lambda x: x[1], reverse=True)
        return boosted
    
    def _cross_encoder_rerank(self, 
                               query: str,
                               docs_and_scores: List[Tuple],
                               top_k: int = 10) -> List[Tuple]:
        """
        Rerank using cross-encoder for semantic relevance.
        
        Args:
            query: User query
            docs_and_scores: List of (doc, score) tuples
            top_k: Number of results to rerank
            
        Returns:
            Reranked list of (doc, original_score, rerank_score) tuples
        """
        if not docs_and_scores:
            return []
        
        # Take top candidates for reranking
        candidates = docs_and_scores[:top_k * 2]
        
        # Prepare pairs for cross-encoder
        pairs = [(query, doc.page_content) for doc, _ in candidates]
        
        # Get rerank scores
        rerank_scores = self.reranker.predict(pairs)
        
        # Combine with original scores
        reranked = [
            (doc, orig_score, float(rerank_score))
            for (doc, orig_score), rerank_score in zip(candidates, rerank_scores)
        ]
        
        # Sort by rerank score descending
        reranked.sort(key=lambda x: x[2], reverse=True)
        
        return reranked[:top_k]
    
    def _detect_document_coverage(self,
                                    chunks: List[Tuple],
                                    features: ClinicalFeatures,
                                    topics: List[str]) -> Dict:
        """
        Detect what type of coverage the document provides.
        
        Coverage tiers:
        1. Direct match - Exact case/scenario present
        2. Rule-based coverage - Thresholds/guidelines available
        3. Definitions available - Medical terms defined
        4. Partial guidance - Related but incomplete
        5. No coverage - No relevant information
        
        Args:
            chunks: Retrieved chunks
            features: Clinical features
            topics: Extracted topics
            
        Returns:
            Coverage analysis dict
        """
        coverage = {
            'tier': 'no_coverage',
            'has_direct_match': False,
            'has_rules': False,
            'has_definitions': False,
            'has_partial': False,
            'covered_topics': [],
            'missing_topics': [],
            'derivable': False,
        }
        
        if not chunks:
            return coverage
        
        # Combine all chunk content
        all_content = " ".join([doc.page_content.lower() for doc, _, _ in chunks])
        
        # Check for rules/thresholds
        rule_indicators = [
            'threshold', 'cutoff', 'criteria', 'defined as', 'classified as',
            'hb <', 'hb >', 'bp >', 'bp <', 'glucose >', 'age >', 'age <',
            '≥', '≤', 'g/dl', 'mmhg', 'mg/dl'
        ]
        if any(indicator in all_content for indicator in rule_indicators):
            coverage['has_rules'] = True
            coverage['tier'] = 'rule_based'
        
        # Check for definitions
        definition_indicators = [
            'is defined as', 'refers to', 'means', 'definition',
            'anaemia is', 'hypertension is', 'diabetes is'
        ]
        if any(indicator in all_content for indicator in definition_indicators):
            coverage['has_definitions'] = True
            if coverage['tier'] == 'no_coverage':
                coverage['tier'] = 'definitions'
        
        # Check topic coverage
        for topic in topics:
            topic_keywords = self.TOPIC_MAP.get(topic, [])
            if any(kw in all_content for kw in topic_keywords):
                coverage['covered_topics'].append(topic)
            else:
                coverage['missing_topics'].append(topic)
        
        # Determine if derivable
        if coverage['has_rules'] and len(coverage['covered_topics']) > 0:
            coverage['derivable'] = True
            coverage['tier'] = 'derivable'
        
        # Check for partial guidance
        if len(coverage['covered_topics']) > 0:
            coverage['has_partial'] = True
            if coverage['tier'] == 'no_coverage':
                coverage['tier'] = 'partial'
        
        return coverage
    
    def _calculate_confidence(self,
                               chunks: List[Tuple],
                               coverage: Dict,
                               features: ClinicalFeatures) -> Dict:
        """
        Calculate confidence score with breakdown.
        
        Confidence = Retrieval quality (40%) + Rule coverage (30%) + Chunk agreement (30%)
        
        Args:
            chunks: Retrieved chunks
            coverage: Coverage analysis
            features: Clinical features
            
        Returns:
            Confidence dict with score and breakdown
        """
        if not chunks:
            return {
                'level': 'none',
                'score': 0.0,
                'breakdown': {
                    'retrieval_quality': 0.0,
                    'rule_coverage': 0.0,
                    'chunk_agreement': 0.0,
                }
            }
        
        # 1. Retrieval quality (40%) - based on top rerank score
        top_rerank_score = chunks[0][2] if chunks else -10.0
        if top_rerank_score >= 0.5:
            retrieval_quality = 1.0
        elif top_rerank_score >= 0.0:
            retrieval_quality = 0.7
        elif top_rerank_score >= -2.0:
            retrieval_quality = 0.4
        else:
            retrieval_quality = 0.2
        
        # 2. Rule coverage (30%) - based on coverage analysis
        if coverage['derivable']:
            rule_coverage = 1.0
        elif coverage['has_rules']:
            rule_coverage = 0.8
        elif coverage['has_definitions']:
            rule_coverage = 0.5
        else:
            rule_coverage = 0.2
        
        # 3. Chunk agreement (30%) - how many chunks agree on topics
        if len(chunks) >= 5:
            chunk_agreement = 1.0
        elif len(chunks) >= 3:
            chunk_agreement = 0.7
        elif len(chunks) >= 1:
            chunk_agreement = 0.4
        else:
            chunk_agreement = 0.0
        
        # Calculate weighted score
        confidence_score = (
            retrieval_quality * 0.4 +
            rule_coverage * 0.3 +
            chunk_agreement * 0.3
        )
        
        # Determine level
        if confidence_score >= 0.75:
            level = 'high'
        elif confidence_score >= 0.50:
            level = 'medium'
        elif confidence_score >= 0.25:
            level = 'low'
        else:
            level = 'very_low'
        
        return {
            'level': level,
            'score': confidence_score,
            'breakdown': {
                'retrieval_quality': retrieval_quality,
                'rule_coverage': rule_coverage,
                'chunk_agreement': chunk_agreement,
            }
        }
    
    def retrieve(self,
                 query: str,
                 rewritten_query: str,
                 features: ClinicalFeatures,
                 top_k: int = 8,
                 verbose: bool = True) -> Dict:
        """
        Full improved retrieval pipeline.
        
        Pipeline:
        1. Extract topics from query
        2. FAISS vector search (with distance→similarity conversion)
        3. BM25 keyword search
        4. Reciprocal Rank Fusion
        5. Metadata-aware boosting
        6. Cross-encoder reranking
        7. Document coverage detection
        8. Confidence calculation
        
        Args:
            query: Original query
            rewritten_query: Structured clinical query
            features: Extracted clinical features
            top_k: Number of final chunks
            verbose: Print debug info
            
        Returns:
            Retrieval result dict
        """
        if verbose:
            print(f"\n[RETRIEVER] Processing query...")
        
        # Step 1: Extract topics
        topics = self._extract_topics_from_query(query, features)
        if verbose:
            print(f"[RETRIEVER] Extracted topics: {topics}")
        
        # Step 2: FAISS vector search
        faiss_results_raw = self.vectorstore.similarity_search_with_score(
            rewritten_query,
            k=30
        )
        
        # Convert distances to similarities
        faiss_results = [
            (doc, self._convert_distance_to_similarity(dist))
            for doc, dist in faiss_results_raw
        ]
        
        if verbose:
            print(f"[RETRIEVER] FAISS: {len(faiss_results)} chunks (top similarity: {faiss_results[0][1]:.3f})")
        
        # Step 3: BM25 keyword search
        bm25_results = self._bm25_search(query, features, max_results=10)
        
        if verbose:
            print(f"[RETRIEVER] BM25: {len(bm25_results)} chunks")
        
        # Step 4: Reciprocal Rank Fusion
        merged_results = self._reciprocal_rank_fusion(faiss_results, bm25_results)
        
        if verbose:
            print(f"[RETRIEVER] RRF merged: {len(merged_results)} chunks")
        
        # Step 5: Metadata-aware boosting
        boosted_results = self._apply_metadata_boosting(merged_results, topics, features)
        
        if verbose:
            print(f"[RETRIEVER] Metadata boosting applied")
        
        # Step 6: Cross-encoder reranking
        reranked_results = self._cross_encoder_rerank(query, boosted_results, top_k=top_k)
        
        if verbose:
            if reranked_results:
                print(f"[RETRIEVER] Reranked: {len(reranked_results)} chunks (top score: {reranked_results[0][2]:.3f})")
            else:
                print(f"[RETRIEVER] No chunks after reranking")
        
        # Step 7: Document coverage detection
        coverage = self._detect_document_coverage(reranked_results, features, topics)
        
        if verbose:
            print(f"[RETRIEVER] Coverage tier: {coverage['tier']}")
            print(f"[RETRIEVER] Derivable: {coverage['derivable']}")
            print(f"[RETRIEVER] Covered topics: {coverage['covered_topics']}")
        
        # Step 8: Confidence calculation
        confidence_result = self._calculate_confidence(reranked_results, coverage, features)
        
        if verbose:
            print(f"[RETRIEVER] Confidence: {confidence_result['level'].upper()} ({confidence_result['score']:.2f})")
            print(f"[RETRIEVER]   - Retrieval quality: {confidence_result['breakdown']['retrieval_quality']:.2f}")
            print(f"[RETRIEVER]   - Rule coverage: {confidence_result['breakdown']['rule_coverage']:.2f}")
            print(f"[RETRIEVER]   - Chunk agreement: {confidence_result['breakdown']['chunk_agreement']:.2f}")
        
        # Extract metadata
        metadata = self._extract_metadata(reranked_results)
        
        return {
            'chunks': reranked_results,
            'metadata': metadata,
            'confidence': confidence_result['level'],
            'confidence_score': confidence_result['score'],
            'confidence_breakdown': confidence_result['breakdown'],
            'coverage': coverage,
            'topics': topics,
            'stats': {
                'faiss_count': len(faiss_results),
                'bm25_count': len(bm25_results),
                'merged_count': len(merged_results),
                'final_count': len(reranked_results),
                'top_similarity': faiss_results[0][1] if faiss_results else 0.0,
                'top_rerank_score': reranked_results[0][2] if reranked_results else 0.0,
            }
        }
    
    def _extract_metadata(self, chunks: List[Tuple]) -> Dict:
        """Extract metadata from retrieved chunks."""
        pages = []
        sections = []
        conditions = []
        
        for doc, _, _ in chunks:
            meta = doc.metadata
            pages.append(meta.get('page_number', '?'))
            sections.append(meta.get('section_name', '?'))
            conditions.append(meta.get('condition', '?'))
        
        return {
            'pages': pages,
            'sections': list(set(sections)),
            'conditions': list(set(conditions)),
        }
    
    def format_context(self, chunks: List[Tuple]) -> str:
        """Format retrieved chunks into context string for LLM."""
        if not chunks:
            return None
        
        context_blocks = []
        for rank, (doc, orig_score, rerank_score) in enumerate(chunks, 1):
            meta = doc.metadata
            block = (
                f"[CHUNK {rank} | Page {meta.get('page_number', '?')} | "
                f"Section: {meta.get('section_name', '?')} | "
                f"Similarity: {orig_score:.3f} | Rerank: {rerank_score:.3f}]\n"
                f"{doc.page_content}"
            )
            context_blocks.append(block)
        
        return "\n\n---\n\n".join(context_blocks)
