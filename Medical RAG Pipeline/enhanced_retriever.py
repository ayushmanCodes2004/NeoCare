# ============================================================
# enhanced_retriever.py — Improved FAISS retrieval with MMR and reranking
# ============================================================
"""
LAYER 3: Enhanced Retrieval System
- Increased top_k for better recall
- Cosine similarity scoring
- Max Marginal Relevance (MMR) for diversity
- Deduplication
- Rule-based reranking with clinical prioritization
- Hybrid keyword fallback
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from sentence_transformers import CrossEncoder
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from clinical_preprocessor import ClinicalFeatures
from config import LOG_FILE

# Note: Other config imports moved to __init__ to avoid issues

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")


class EnhancedRetriever:
    """
    Enhanced retrieval system with clinical awareness.
    Integrates with clinical preprocessor for feature-aware retrieval.
    """
    
    def __init__(self, index_dir: str = None):
        """Initialize retriever with FAISS index and reranker."""
        # Import config here to get default index directory
        from config import FAISS_INDEX_DIR, EMBEDDING_MODEL, OPENAI_API_KEY
        
        if index_dir is None:
            index_dir = FAISS_INDEX_DIR
        
        self.index_dir = index_dir
        
        # Load cross-encoder reranker
        print("[RETRIEVER] Loading cross-encoder reranker...")
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        print("[RETRIEVER] Reranker loaded.")
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Load FAISS index
        self.vectorstore = FAISS.load_local(
            self.index_dir, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
    
    def retrieve(self, 
                 query: str,
                 rewritten_query: str,
                 features: ClinicalFeatures,
                 top_k: int = 10,
                 use_mmr: bool = True,
                 verbose: bool = True) -> Dict:
        """
        Enhanced retrieval pipeline with clinical awareness.
        
        Args:
            query: Original user query
            rewritten_query: Clinically rewritten query
            features: Extracted clinical features
            top_k: Number of final chunks to return
            use_mmr: Use Max Marginal Relevance for diversity
            verbose: Print debug information
            
        Returns:
            Dict with retrieved chunks, scores, and metadata
        """
        if verbose:
            print(f"\n[RETRIEVER] Original query: {query[:100]}...")
            print(f"[RETRIEVER] Rewritten query: {rewritten_query[:100]}...")
        
        # STEP 1: Initial FAISS retrieval (increased fetch_k for better recall)
        fetch_k = 30  # Fetch more candidates initially
        
        if use_mmr:
            # Use MMR for diversity (reduces redundant chunks)
            try:
                docs_and_scores = self.vectorstore.max_marginal_relevance_search_with_score(
                    rewritten_query,
                    k=top_k * 2,  # Fetch 2x for reranking
                    fetch_k=fetch_k,
                    lambda_mult=0.7  # Balance relevance (1.0) vs diversity (0.0)
                )
            except AttributeError:
                # Fallback if MMR not available
                docs_and_scores = self.vectorstore.similarity_search_with_score(
                    rewritten_query, 
                    k=fetch_k
                )
        else:
            docs_and_scores = self.vectorstore.similarity_search_with_score(
                rewritten_query, 
                k=fetch_k
            )
        
        if verbose:
            print(f"[RETRIEVER] Stage 1: Fetched {len(docs_and_scores)} chunks from FAISS")
        
        # STEP 2: Hybrid keyword search fallback
        keyword_results = self._keyword_search(query, features, max_results=5)
        
        # Merge keyword results (avoid duplicates)
        seen_contents = set(doc.page_content[:100] for doc, _ in docs_and_scores)
        keyword_injected = 0
        for kw_doc, kw_score in keyword_results:
            if kw_doc.page_content[:100] not in seen_contents:
                docs_and_scores.append((kw_doc, kw_score))
                seen_contents.add(kw_doc.page_content[:100])
                keyword_injected += 1
        
        if verbose and keyword_injected > 0:
            print(f"[RETRIEVER] Hybrid: Injected {keyword_injected} keyword-matched chunks")
        
        # STEP 3: Deduplication (remove near-duplicate chunks)
        docs_and_scores = self._deduplicate_chunks(docs_and_scores)
        
        if verbose:
            print(f"[RETRIEVER] After deduplication: {len(docs_and_scores)} chunks")
        
        # STEP 4: Cross-encoder reranking
        if len(docs_and_scores) > 0:
            pairs = [(query, doc.page_content) for doc, _ in docs_and_scores]
            rerank_scores = self.reranker.predict(pairs)
            
            # Combine with original scores
            ranked = list(zip(
                [doc for doc, _ in docs_and_scores],
                [score for _, score in docs_and_scores],
                rerank_scores
            ))
            
            # Sort by rerank score (descending)
            ranked.sort(key=lambda x: x[2], reverse=True)
            
            if verbose:
                print(f"[RETRIEVER] Cross-encoder reranking complete")
                print(f"[RETRIEVER] Top rerank score: {ranked[0][2]:.3f}")
        else:
            ranked = []
        
        # STEP 5: Clinical rule-based reranking boost
        ranked = self._apply_clinical_reranking(ranked, features, verbose=verbose)
        
        # STEP 6: Select top_k final chunks
        final_chunks = ranked[:top_k]
        
        # STEP 7: Extract metadata
        metadata = self._extract_metadata(final_chunks)
        
        if verbose:
            print(f"[RETRIEVER] Final: {len(final_chunks)} chunks selected")
            print(f"[RETRIEVER] Pages used: {metadata['pages']}")
        
        # STEP 8: Determine confidence
        confidence = self._determine_confidence(final_chunks)
        
        if verbose:
            print(f"[RETRIEVER] Confidence: {confidence.upper()}")
        
        return {
            'chunks': final_chunks,
            'metadata': metadata,
            'confidence': confidence,
            'stats': {
                'initial_fetch': fetch_k,
                'after_dedup': len(docs_and_scores),
                'keyword_injected': keyword_injected,
                'final_count': len(final_chunks),
                'top_rerank_score': final_chunks[0][2] if final_chunks else 0.0,
            }
        }
    
    def _keyword_search(self, query: str, features: ClinicalFeatures, 
                        max_results: int = 5) -> List[Tuple]:
        """
        Keyword-based fallback search with clinical awareness.
        Prioritizes keywords based on extracted features.
        """
        keywords = set()
        query_lower = query.lower()
        
        # Add feature-specific keywords
        if features.age_risk_category == "advanced_maternal_age":
            keywords.update(['advanced maternal age', 'elderly gravida', 'age 35', 'age over 35'])
        elif features.age_risk_category == "teenage_pregnancy":
            keywords.update(['teenage', 'adolescent', 'young age'])
        
        if features.anemia_risk and "anemia" in features.anemia_risk:
            keywords.update(['anaemia', 'anemia', 'hemoglobin', 'haemoglobin', 'iron', 'IFA'])
        
        if features.bp_risk == "hypertensive":
            keywords.update(['hypertension', 'pre-eclampsia', 'blood pressure', 'PIH'])
        
        if features.glucose_risk and "diabet" in features.glucose_risk:
            keywords.update(['diabetes', 'GDM', 'glucose', 'OGTT', 'insulin'])
        
        # Add query words
        query_words = set(word for word in query_lower.split() if len(word) > 3)
        keywords.update(query_words)
        
        # Search through docstore
        scored_docs = []
        docstore = self.vectorstore.docstore._dict
        
        for doc_id, doc in docstore.items():
            text_lower = doc.page_content.lower()
            match_count = sum(1 for kw in keywords if kw in text_lower)
            if match_count >= 2:
                scored_docs.append((doc, match_count))
        
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:max_results]
    
    def _deduplicate_chunks(self, docs_and_scores: List[Tuple], 
                            similarity_threshold: float = 0.85) -> List[Tuple]:
        """
        Remove near-duplicate chunks based on content similarity.
        Uses simple character overlap for efficiency.
        """
        if not docs_and_scores:
            return []
        
        unique_chunks = []
        seen_contents = []
        
        for doc, score in docs_and_scores:
            content = doc.page_content
            is_duplicate = False
            
            for seen_content in seen_contents:
                # Simple overlap check
                overlap = len(set(content[:200]) & set(seen_content[:200]))
                if overlap / max(len(content[:200]), len(seen_content[:200])) > similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_chunks.append((doc, score))
                seen_contents.append(content)
        
        return unique_chunks
    
    def _apply_clinical_reranking(self, ranked: List[Tuple], 
                                   features: ClinicalFeatures,
                                   verbose: bool = False) -> List[Tuple]:
        """
        Apply rule-based reranking boost based on clinical features.
        
        This prevents retrieval bias:
        - Boost age-risk chunks ONLY if age >= 35
        - Boost anemia chunks ONLY if Hb < 11
        - Boost hypertension chunks ONLY if BP high
        """
        if not ranked:
            return ranked
        
        boosted_ranked = []
        
        for doc, l2_score, rerank_score in ranked:
            content_lower = doc.page_content.lower()
            boost = 0.0
            
            # Age-based boosting
            if features.age_risk_category == "advanced_maternal_age":
                if any(term in content_lower for term in ['advanced maternal age', 'elderly', 'age 35', 'age over 35']):
                    boost += 0.15
                    if verbose:
                        print(f"[RERANK] Boosted age-risk chunk: {doc.page_content[:60]}...")
            
            # Anemia boosting (ONLY if Hb is actually low)
            if features.anemia_risk and "anemia" in features.anemia_risk:
                if any(term in content_lower for term in ['anaemia', 'anemia', 'hemoglobin', 'haemoglobin']):
                    boost += 0.12
                    if verbose:
                        print(f"[RERANK] Boosted anemia chunk: {doc.page_content[:60]}...")
            
            # Hypertension boosting (ONLY if BP is high)
            if features.bp_risk == "hypertensive":
                if any(term in content_lower for term in ['hypertension', 'pre-eclampsia', 'blood pressure', 'pih']):
                    boost += 0.12
                    if verbose:
                        print(f"[RERANK] Boosted hypertension chunk: {doc.page_content[:60]}...")
            
            # Diabetes boosting
            if features.glucose_risk and "diabet" in features.glucose_risk:
                if any(term in content_lower for term in ['diabetes', 'gdm', 'glucose', 'insulin']):
                    boost += 0.12
            
            # Obstetric history boosting
            if features.twin_pregnancy and 'twin' in content_lower:
                boost += 0.10
            if features.previous_cesarean and any(term in content_lower for term in ['caesarean', 'cesarean', 'lscs']):
                boost += 0.10
            if features.placenta_previa and 'placenta' in content_lower:
                boost += 0.15
            
            # Apply boost
            boosted_score = rerank_score + boost
            boosted_ranked.append((doc, l2_score, boosted_score))
        
        # Re-sort by boosted score
        boosted_ranked.sort(key=lambda x: x[2], reverse=True)
        
        return boosted_ranked
    
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
    
    def _determine_confidence(self, chunks: List[Tuple]) -> str:
        """
        Determine confidence level based on retrieval quality.
        
        Criteria:
        - High: Top score >= 0.3, at least 3 chunks
        - Medium: Top score >= 0.1, at least 2 chunks
        - Low: Otherwise
        """
        if not chunks:
            return "low"
        
        top_score = chunks[0][2]
        num_chunks = len(chunks)
        
        if top_score >= 0.3 and num_chunks >= 3:
            return "high"
        elif top_score >= 0.1 and num_chunks >= 2:
            return "medium"
        else:
            return "low"
    
    def format_context(self, chunks: List[Tuple]) -> str:
        """Format retrieved chunks into context string for LLM."""
        if not chunks:
            return None
        
        context_blocks = []
        for rank, (doc, l2_score, rerank_score) in enumerate(chunks, 1):
            meta = doc.metadata
            block = (
                f"[CHUNK {rank} | Page {meta.get('page_number', '?')} | "
                f"Section: {meta.get('section_name', '?')} | "
                f"Rerank Score: {rerank_score:.3f}]\n"
                f"{doc.page_content}"
            )
            context_blocks.append(block)
        
        return "\n\n---\n\n".join(context_blocks)
