# ============================================================
# layer2_retrieval.py — Hybrid Retrieval System
# ============================================================
"""
LAYER 2: Hybrid Retrieval

Implements:
- Dense retrieval (FAISS with L2 normalization)
- Sparse retrieval (BM25 keyword search)
- Reciprocal Rank Fusion
- Cross-encoder reranking
- Score normalization (distance → similarity)
- Query rewriting (structured format)
"""

import re
import numpy as np
from typing import List, Dict, Tuple
from collections import Counter
from sentence_transformers import CrossEncoder
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from layer1_extractor import ClinicalFeatures
from config_production import (
    FAISS_INDEX_DIR, EMBEDDING_MODEL, OLLAMA_BASE_URL,
    FAISS_TOP_K, BM25_TOP_K, RERANK_TOP_K, RERANK_MODEL,
    MIN_SIMILARITY_THRESHOLD, CLINICAL_TAGS
)


class HybridRetriever:
    """
    Production-grade hybrid retrieval system.
    Combines FAISS + BM25 + Cross-encoder reranking.
    """
    
    def __init__(self, index_dir: str = None):
        """Initialize hybrid retriever."""
        if index_dir is None:
            index_dir = FAISS_INDEX_DIR
        
        print("[RETRIEVER] Initializing hybrid retrieval system...")
        
        # Load cross-encoder reranker
        print(f"[RETRIEVER] Loading cross-encoder: {RERANK_MODEL}")
        self.reranker = CrossEncoder(RERANK_MODEL)
        
        # Initialize embeddings
        self.embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL
        )
        
        # Load FAISS index
        print(f"[RETRIEVER] Loading FAISS index from: {index_dir}")
        self.vectorstore = FAISS.load_local(
            index_dir,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        print("[RETRIEVER] Hybrid retriever ready")
    
    def retrieve(self,
                 query: str,
                 features: ClinicalFeatures,
                 verbose: bool = False) -> Dict:
        """
        Full hybrid retrieval pipeline.
        
        Args:
            query: Original user query
            features: Extracted clinical features
            verbose: Print retrieval details
            
        Returns:
            Dict with chunks, scores, and quality metrics
        """
        if verbose:
            print("\n[RETRIEVAL] Starting hybrid retrieval...")
        
        # Step 1: Query rewriting (structured format)
        rewritten_query = self._rewrite_query(query, features, verbose)
        
        # Step 2: FAISS dense retrieval
        faiss_results = self._faiss_retrieval(rewritten_query, verbose)
        
        # Step 3: BM25 sparse retrieval
        bm25_results = self._bm25_retrieval(query, features, verbose)
        
        # Step 4: Reciprocal Rank Fusion
        merged_results = self._reciprocal_rank_fusion(
            faiss_results, bm25_results, verbose
        )
        
        # Step 5: Cross-encoder reranking
        reranked_results = self._cross_encoder_rerank(
            query, merged_results, verbose
        )
        
        # Step 6: Calculate quality metrics
        retrieval_quality = self._calculate_retrieval_quality(reranked_results)
        chunk_agreement = self._calculate_chunk_agreement(reranked_results, features)
        
        if verbose:
            print(f"[RETRIEVAL] Retrieval Quality: {retrieval_quality:.2f}")
            print(f"[RETRIEVAL] Chunk Agreement: {chunk_agreement:.2f}")
        
        return {
            'chunks': reranked_results,
            'rewritten_query': rewritten_query,
            'retrieval_quality': retrieval_quality,
            'chunk_agreement': chunk_agreement,
            'faiss_count': len(faiss_results),
            'bm25_count': len(bm25_results),
            'final_count': len(reranked_results),
        }
    
    def _rewrite_query(self,
                       query: str,
                       features: ClinicalFeatures,
                       verbose: bool) -> str:
        """
        Rewrite query into structured format for better retrieval.
        
        Example:
        "38-year-old with BP 150/95, Hb 10.5"
        →
        "Advanced maternal age pregnancy risk classification India guidelines
         Hypertension BP 150/95 management pregnancy
         Anaemia Hb 10.5 threshold pregnancy"
        """
        parts = []
        
        # Age-based terms
        if features.age:
            if features.age >= 35:
                parts.append("Advanced maternal age pregnancy risk classification India guidelines")
            elif features.age < 18:
                parts.append("Teenage pregnancy adolescent maternal health risks")
        
        # BP-based terms
        if features.systolic_bp and features.diastolic_bp:
            if features.systolic_bp >= 140 or features.diastolic_bp >= 90:
                parts.append(f"Hypertension BP {features.systolic_bp}/{features.diastolic_bp} management pregnancy pre-eclampsia")
            else:
                parts.append("Blood pressure normal pregnancy monitoring")
        
        # Hb-based terms
        if features.hemoglobin:
            if features.hemoglobin < 11:
                parts.append(f"Anaemia Hb {features.hemoglobin} anemia threshold pregnancy iron supplementation")
            else:
                parts.append("Haemoglobin normal pregnancy")
        
        # Glucose-based terms
        if features.fbs:
            if features.fbs >= 92:
                parts.append(f"Gestational diabetes GDM glucose {features.fbs} management pregnancy")
            else:
                parts.append("Blood glucose normal pregnancy")
        
        # Obstetric history
        if features.twin_pregnancy:
            parts.append("Twin pregnancy multiple gestation high risk management")
        if features.prior_cesarean:
            parts.append("Previous cesarean section LSCS uterine rupture risk")
        if features.placenta_previa:
            parts.append("Placenta previa antepartum hemorrhage management")
        
        # Add original query
        parts.append(query)
        
        rewritten = " ".join(parts)
        
        if verbose:
            print(f"[RETRIEVAL] Rewritten query: {rewritten[:150]}...")
        
        return rewritten
    
    def _faiss_retrieval(self, query: str, verbose: bool) -> List[Tuple]:
        """
        FAISS dense retrieval with score normalization.
        
        Converts L2 distance → similarity [0, 1]
        """
        # Fetch from FAISS
        docs_and_distances = self.vectorstore.similarity_search_with_score(
            query, k=FAISS_TOP_K
        )
        
        # Convert distances to similarities
        results = []
        for doc, distance in docs_and_distances:
            # L2 distance → similarity: similarity = 1 / (1 + distance)
            similarity = 1.0 / (1.0 + distance)
            results.append((doc, similarity))
        
        if verbose:
            print(f"[RETRIEVAL] FAISS: {len(results)} chunks (top similarity: {results[0][1]:.3f})")
        
        return results
    
    def _bm25_retrieval(self,
                        query: str,
                        features: ClinicalFeatures,
                        verbose: bool) -> List[Tuple]:
        """
        BM25-style keyword search for exact matches.
        """
        # Extract keywords
        keywords = set()
        query_words = [w.lower() for w in query.split() if len(w) > 3]
        keywords.update(query_words)
        
        # Add feature-specific keywords
        if features.age:
            keywords.add(str(features.age))
            if features.age >= 35:
                keywords.update(['advanced', 'maternal', 'age', 'elderly', '35'])
        
        if features.hemoglobin:
            keywords.add(str(features.hemoglobin))
            keywords.update(['hemoglobin', 'haemoglobin', 'hb', 'anaemia', 'anemia'])
        
        if features.systolic_bp:
            keywords.add(str(features.systolic_bp))
            keywords.update(['blood', 'pressure', 'bp', 'hypertension'])
        
        if features.fbs:
            keywords.add(str(features.fbs))
            keywords.update(['glucose', 'diabetes', 'fbs', 'gdm'])
        
        # Search docstore
        scored_docs = []
        docstore = self.vectorstore.docstore._dict
        
        for doc_id, doc in docstore.items():
            text_lower = doc.page_content.lower()
            
            # Count keyword matches
            match_count = 0
            for kw in keywords:
                if kw in text_lower:
                    freq = min(text_lower.count(kw), 3)
                    match_count += freq
            
            if match_count >= 2:
                # BM25-style score
                doc_length = len(text_lower.split())
                avg_doc_length = 200
                score = match_count / (1 + abs(doc_length - avg_doc_length) / avg_doc_length)
                scored_docs.append((doc, score))
        
        # Sort and take top-k
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        results = scored_docs[:BM25_TOP_K]
        
        if verbose:
            print(f"[RETRIEVAL] BM25: {len(results)} chunks")
        
        return results
    
    def _reciprocal_rank_fusion(self,
                                 faiss_results: List[Tuple],
                                 bm25_results: List[Tuple],
                                 verbose: bool,
                                 k: int = 60) -> List[Tuple]:
        """
        Merge FAISS and BM25 using Reciprocal Rank Fusion.
        
        RRF formula: score = sum(1 / (k + rank))
        """
        rrf_scores = {}
        doc_map = {}
        
        # Add FAISS results
        for rank, (doc, _) in enumerate(faiss_results, 1):
            doc_id = id(doc)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank)
            doc_map[doc_id] = doc
        
        # Add BM25 results
        for rank, (doc, _) in enumerate(bm25_results, 1):
            doc_id = id(doc)
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (k + rank)
            doc_map[doc_id] = doc
        
        # Sort by RRF score
        merged = [(doc_map[doc_id], score) for doc_id, score in rrf_scores.items()]
        merged.sort(key=lambda x: x[1], reverse=True)
        
        if verbose:
            print(f"[RETRIEVAL] RRF merged: {len(merged)} unique chunks")
        
        return merged
    
    def _cross_encoder_rerank(self,
                               query: str,
                               merged_results: List[Tuple],
                               verbose: bool) -> List[Tuple]:
        """
        Rerank using cross-encoder for semantic relevance.
        Normalizes scores to [0, 1] range.
        """
        if not merged_results:
            return []
        
        # Take top candidates for reranking
        candidates = merged_results[:RERANK_TOP_K * 2]
        
        # Prepare pairs
        pairs = [(query, doc.page_content) for doc, _ in candidates]
        
        # Get rerank scores (can be negative)
        rerank_scores = self.reranker.predict(pairs)
        
        # Normalize scores: normalized = 1 / (1 + abs(score))
        # This converts negative scores to positive [0, 1] range
        normalized_scores = [
            1.0 / (1.0 + abs(float(score)))
            for score in rerank_scores
        ]
        
        # Combine
        reranked = [
            (doc, normalized_score)
            for (doc, _), normalized_score in zip(candidates, normalized_scores)
        ]
        
        # Sort by normalized score
        reranked.sort(key=lambda x: x[1], reverse=True)
        
        # Apply MMR for diversity
        mmr_results = self._apply_mmr(query, reranked, verbose)
        
        if verbose:
            if mmr_results:
                print(f"[RETRIEVAL] Reranked: {len(mmr_results)} chunks (top score: {mmr_results[0][1]:.3f})")
            else:
                print(f"[RETRIEVAL] No chunks after reranking")
        
        return mmr_results
    
    def _apply_mmr(self,
                   query: str,
                   reranked_results: List[Tuple],
                   verbose: bool,
                   lambda_param: float = 0.7,
                   top_k: int = None) -> List[Tuple]:
        """
        Apply Maximal Marginal Relevance for diversity.
        
        MMR balances relevance and diversity:
        MMR = λ * relevance(doc, query) - (1-λ) * max_similarity(doc, selected_docs)
        
        Args:
            query: Search query
            reranked_results: Documents with relevance scores
            verbose: Print debug info
            lambda_param: Balance between relevance (1.0) and diversity (0.0)
            top_k: Number of documents to return
            
        Returns:
            List of (doc, score) tuples with diversity
        """
        if not reranked_results:
            return []
        
        if top_k is None:
            top_k = RERANK_TOP_K
        
        # Get embeddings for all documents
        docs = [doc for doc, _ in reranked_results]
        relevance_scores = [score for _, score in reranked_results]
        
        # Get document embeddings
        doc_texts = [doc.page_content for doc in docs]
        doc_embeddings = np.array([
            self.embeddings.embed_query(text) for text in doc_texts
        ])
        
        # Get query embedding
        query_embedding = np.array(self.embeddings.embed_query(query))
        
        # Normalize embeddings
        doc_embeddings = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Calculate relevance scores (cosine similarity with query)
        relevance_to_query = np.dot(doc_embeddings, query_embedding)
        
        # MMR selection
        selected_indices = []
        selected_embeddings = []
        remaining_indices = list(range(len(docs)))
        
        # Select first document (highest relevance)
        first_idx = np.argmax(relevance_to_query)
        selected_indices.append(first_idx)
        selected_embeddings.append(doc_embeddings[first_idx])
        remaining_indices.remove(first_idx)
        
        # Select remaining documents using MMR
        while len(selected_indices) < top_k and remaining_indices:
            mmr_scores = []
            
            for idx in remaining_indices:
                # Relevance component
                relevance = relevance_to_query[idx]
                
                # Diversity component (max similarity to selected docs)
                if selected_embeddings:
                    similarities = [
                        np.dot(doc_embeddings[idx], selected_emb)
                        for selected_emb in selected_embeddings
                    ]
                    max_similarity = max(similarities)
                else:
                    max_similarity = 0.0
                
                # MMR score
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity
                mmr_scores.append((idx, mmr_score))
            
            # Select document with highest MMR score
            if mmr_scores:
                best_idx, best_score = max(mmr_scores, key=lambda x: x[1])
                selected_indices.append(best_idx)
                selected_embeddings.append(doc_embeddings[best_idx])
                remaining_indices.remove(best_idx)
            else:
                break
        
        # Build final results with original relevance scores
        mmr_results = [
            (docs[idx], relevance_scores[idx])
            for idx in selected_indices
        ]
        
        if verbose:
            diversity_gain = len(set(selected_indices)) / len(selected_indices) if selected_indices else 0
            print(f"[RETRIEVAL] MMR applied: {len(mmr_results)} diverse chunks (λ={lambda_param})")
        
        return mmr_results
    
    def _calculate_retrieval_quality(self, chunks: List[Tuple]) -> float:
        """
        Calculate retrieval quality: avg top-3 similarity with spread penalty.
        
        Formula: avg(top-3 scores) * (1 - spread_penalty)
        """
        if not chunks:
            return 0.0
        
        # Get top-3 scores
        top_scores = [score for _, score in chunks[:3]]
        
        if not top_scores:
            return 0.0
        
        # Average score
        avg_score = sum(top_scores) / len(top_scores)
        
        # Penalize low spread (all scores similar = less confident)
        if len(top_scores) > 1:
            spread = max(top_scores) - min(top_scores)
            spread_penalty = 0.1 if spread < 0.1 else 0.0
        else:
            spread_penalty = 0.0
        
        quality = avg_score * (1 - spread_penalty)
        
        # Normalize to [0, 1]
        quality = max(0.0, min(1.0, quality))
        
        return quality
    
    def _calculate_chunk_agreement(self,
                                    chunks: List[Tuple],
                                    features: ClinicalFeatures) -> float:
        """
        Calculate chunk agreement: do multiple chunks support same findings?
        
        Checks if clinical terms appear in multiple chunks.
        """
        if len(chunks) < 2:
            return 0.5  # Neutral if only 1 chunk
        
        # Extract clinical terms from features
        terms = []
        if features.age and features.age >= 35:
            terms.extend(['advanced maternal age', 'elderly', 'age 35'])
        if features.hemoglobin and features.hemoglobin < 11:
            terms.extend(['anaemia', 'anemia', 'hemoglobin'])
        if features.systolic_bp and features.systolic_bp >= 140:
            terms.extend(['hypertension', 'blood pressure'])
        if features.fbs and features.fbs >= 92:
            terms.extend(['diabetes', 'gdm', 'glucose'])
        
        if not terms:
            return 0.7  # No specific terms to check
        
        # Count how many chunks contain each term
        term_counts = {term: 0 for term in terms}
        for doc, _ in chunks:
            content_lower = doc.page_content.lower()
            for term in terms:
                if term in content_lower:
                    term_counts[term] += 1
        
        # Agreement = avg % of chunks containing each term
        agreements = [count / len(chunks) for count in term_counts.values()]
        
        if not agreements:
            return 0.7
        
        return sum(agreements) / len(agreements)
    
    def format_context(self, chunks: List[Tuple]) -> str:
        """Format chunks into context string for LLM."""
        if not chunks:
            return None
        
        context_blocks = []
        for rank, (doc, score) in enumerate(chunks, 1):
            meta = doc.metadata
            block = (
                f"[CHUNK {rank} | Page {meta.get('page_number', '?')} | "
                f"Section: {meta.get('section_name', '?')} | "
                f"Score: {score:.3f}]\n"
                f"{doc.page_content}"
            )
            context_blocks.append(block)
        
        return "\n\n---\n\n".join(context_blocks)
