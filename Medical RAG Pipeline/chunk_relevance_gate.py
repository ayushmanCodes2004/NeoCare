# ============================================================
# chunk_relevance_gate.py — Step 3.5: Chunk Relevance Gate
# ============================================================
"""
STEP 3.5: Chunk Relevance Gate

Filters retrieved chunks to ensure they match CONFIRMED conditions only.

Prevents:
- GDM chunks reaching generation for non-diabetic patients
- Thyroid chunks for patients without thyroid disorder
- Irrelevant topic contamination

Logic:
1. Identify confirmed conditions from query (with negation awareness)
2. Map chunks to topics using keywords
3. Filter: Keep only chunks matching confirmed conditions
4. Discard chunks from negated or absent conditions
"""

import re
from typing import List, Tuple, Set, Dict
from langchain.schema import Document


class ChunkRelevanceGate:
    """
    Filters chunks based on confirmed patient conditions.
    Prevents topic contamination in retrieval.
    """
    
    # Topic markers for chunk classification
    TOPIC_MARKERS = {
        'gdm': [
            'gestational diabetes', 'gdm', 'blood glucose level',
            'insulin dose', 'ogtt', 'pppg', 'fasting blood sugar',
            'glucose monitoring', 'diabetic pregnancy'
        ],
        'hypertension': [
            'hypertension', 'blood pressure', 'bp ≥', 'pre-eclampsia',
            'eclampsia', 'antihypertensive', 'alpha methyl dopa',
            'nifedipine', 'labetalol', 'mgso4'
        ],
        'anaemia': [
            'anaemia', 'anemia', 'hemoglobin', 'haemoglobin', 'hb level',
            'ifa tablet', 'iron supplementation', 'blood transfusion'
        ],
        'hypothyroid': [
            'hypothyroidism', 'hypothyroid', 'thyroid', 'tsh level',
            'levothyroxine', 'thyroid disorder'
        ],
        'iugr': [
            'iugr', 'intrauterine growth', 'fetal growth restriction',
            'fundal height', 'sfh', 'small for gestational age'
        ],
        'twins': [
            'twin pregnancy', 'multiple gestation', 'twins',
            'dichorionic', 'monochorionic'
        ],
        'previous_cesarean': [
            'previous cesarean', 'previous lscs', 'uterine scar',
            'vbac', 'repeat cesarean'
        ],
        'placenta_previa': [
            'placenta previa', 'placenta praevia', 'low lying placenta',
            'antepartum hemorrhage'
        ]
    }
    
    # Negation patterns
    NEGATION_PATTERNS = [
        r'no\s+history\s+of\s+([\w\s,]+)',
        r'no\s+known\s+([\w\s,]+)',
        r'denies\s+([\w\s,]+)',
        r'without\s+([\w\s,]+)',
        r'no\s+([\w\s,]+)\s+history',
        r'not\s+([\w\s,]+)',
        r'negative\s+for\s+([\w\s,]+)'
    ]
    
    def __init__(self, verbose: bool = False):
        """Initialize chunk relevance gate."""
        self.verbose = verbose
    
    def filter_chunks(self,
                      chunks: List[Tuple[Document, float]],
                      query: str,
                      extracted_features: Dict = None) -> List[Tuple[Document, float]]:
        """
        Filter chunks to keep only those matching confirmed conditions.
        
        Args:
            chunks: Retrieved chunks with scores
            query: Original clinical query
            extracted_features: Extracted clinical features (optional)
            
        Returns:
            Filtered chunks matching confirmed conditions only
        """
        if self.verbose:
            print(f"\n[CHUNK GATE] Filtering {len(chunks)} chunks...")
        
        # Step 1: Identify confirmed conditions
        confirmed_conditions = self._identify_confirmed_conditions(query, extracted_features)
        
        if self.verbose:
            print(f"[CHUNK GATE] Confirmed conditions: {confirmed_conditions}")
        
        # Step 2: Classify each chunk by topic
        chunk_topics = self._classify_chunks(chunks)
        
        # Step 3: Filter chunks
        filtered_chunks = []
        discarded_count = 0
        
        for (doc, score), topics in zip(chunks, chunk_topics):
            # Keep chunk if:
            # 1. It matches a confirmed condition, OR
            # 2. It's a general/multi-topic chunk (no specific topic markers)
            
            if not topics:
                # General chunk, keep it
                filtered_chunks.append((doc, score))
            elif any(topic in confirmed_conditions for topic in topics):
                # Matches confirmed condition, keep it
                filtered_chunks.append((doc, score))
            else:
                # Doesn't match any confirmed condition, discard
                discarded_count += 1
                if self.verbose:
                    print(f"[CHUNK GATE] ❌ Discarded chunk (topics: {topics}, not in confirmed)")
        
        if self.verbose:
            print(f"[CHUNK GATE] Kept {len(filtered_chunks)}/{len(chunks)} chunks")
            print(f"[CHUNK GATE] Discarded {discarded_count} irrelevant chunks")
        
        return filtered_chunks
    
    def _identify_confirmed_conditions(self,
                                       query: str,
                                       extracted_features: Dict = None) -> Set[str]:
        """
        Identify confirmed conditions from query with negation awareness.
        
        Returns set of confirmed condition names.
        """
        query_lower = query.lower()
        confirmed = set()
        
        # Extract negated terms
        negated_terms = set()
        for pattern in self.NEGATION_PATTERNS:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                negated_terms.add(match.strip())
        
        negated_text = ' '.join(negated_terms)
        
        # Check each condition
        for condition, keywords in self.TOPIC_MARKERS.items():
            # Check if condition is mentioned in query
            condition_mentioned = any(kw in query_lower for kw in keywords)
            
            # Check if condition is negated
            condition_negated = any(kw in negated_text for kw in keywords)
            
            # Confirm if mentioned but not negated
            if condition_mentioned and not condition_negated:
                confirmed.add(condition)
        
        # Add conditions from extracted features if available
        if extracted_features:
            if extracted_features.get('hemoglobin') and extracted_features['hemoglobin'] < 11:
                confirmed.add('anaemia')
            if extracted_features.get('systolic_bp') and extracted_features['systolic_bp'] >= 140:
                confirmed.add('hypertension')
            if extracted_features.get('fbs') and extracted_features['fbs'] >= 92:
                confirmed.add('gdm')
            if extracted_features.get('twin_pregnancy'):
                confirmed.add('twins')
            if extracted_features.get('prior_cesarean'):
                confirmed.add('previous_cesarean')
            if extracted_features.get('placenta_previa'):
                confirmed.add('placenta_previa')
        
        # Always include general pregnancy topics
        confirmed.add('general_pregnancy')
        
        return confirmed
    
    def _classify_chunks(self, chunks: List[Tuple[Document, float]]) -> List[Set[str]]:
        """
        Classify each chunk by topic using keyword matching.
        
        Returns list of topic sets, one per chunk.
        """
        chunk_topics = []
        
        for doc, _ in chunks:
            text_lower = doc.page_content.lower()
            topics = set()
            
            # Check each topic
            for topic, keywords in self.TOPIC_MARKERS.items():
                # Count keyword matches
                match_count = sum(1 for kw in keywords if kw in text_lower)
                
                # If multiple keywords match, classify as this topic
                if match_count >= 2:
                    topics.add(topic)
            
            chunk_topics.append(topics)
        
        return chunk_topics


def apply_chunk_relevance_gate(chunks: List[Tuple[Document, float]],
                                query: str,
                                extracted_features: Dict = None,
                                verbose: bool = False) -> List[Tuple[Document, float]]:
    """
    Convenience function to apply chunk relevance gate.
    
    Args:
        chunks: Retrieved chunks
        query: Clinical query
        extracted_features: Extracted features dict
        verbose: Print filtering details
        
    Returns:
        Filtered chunks
    """
    gate = ChunkRelevanceGate(verbose=verbose)
    return gate.filter_chunks(chunks, query, extracted_features)
