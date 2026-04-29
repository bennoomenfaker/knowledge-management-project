"""
Document Intelligence Engine - NO Cloud AI
Uses: TF-IDF, PostgreSQL Full-Text Search, Section Parsing
"""
import re
import math
from typing import List, Dict, Optional, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class DocumentIntelligenceEngine:
    """
    Non-AI engine for document search and section extraction.
    Works even when all AI providers are down.
    """
    
    # Section headers in French PFE documents
    SECTION_PATTERNS = {
        "problematic": [
            r"probl[èe]matique[:\s]",
            r"probl[èe]me[:\s]",
            r"question\s+de\s+recherche",
        ],
        "solution": [
            r"solution[s]?[:\s]",
            r"r[ée]sultats?[:\s]",
            r"contribution[s]?[:\s]",
            r"apport[s]?[:\s]",
        ],
        "conclusion": [
            r"conclusion[:\s]",
            r"synth[èe]se[:\s]",
        ],
        "methodology": [
            r"m[ée]thodologie[:\s]",
            r"approche\s+m[ée]thodologique",
        ],
        "state_of_art": [
            r"[ée]tat\s+de\s+l['\"]?art",
            r"revue\s+de\s+litt[ée]rature",
        ]
    }
    
    def extract_sections(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract main sections from PFE text using pattern matching.
        Returns: {problematic, solution, conclusion, methodology, state_of_art}
        """
        text_lower = text.lower()
        results = {}
        
        for section, patterns in self.SECTION_PATTERNS.items():
            content = self._extract_section_content(text, text_lower, patterns)
            results[section] = content
        
        return results
    
    def _extract_section_content(self, full_text: str, text_lower: str, patterns: List[str]) -> Optional[str]:
        """Extract content after a section header"""
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                start = match.end()
                # Find next section or take 2000 chars
                end = self._find_next_section(text_lower, start)
                content = full_text[start:end].strip()
                return content[:2000] if content else None
        return None
    
    def _find_next_section(self, text: str, start: int) -> int:
        """Find the next section header after position start"""
        section_headers = [
            "problématique", "problème", "solution", "résultats", "conclusion",
            "méthodologie", "état de l'art", "bibliographie", "références",
            "introduction", "chapitre", "annexe"
        ]
        min_pos = len(text)
        for header in section_headers:
            pos = text.find(header, start + 10)
            if pos != -1 and pos < min_pos:
                min_pos = pos
        return min_pos if min_pos < len(text) else start + 2000
    
    def calculate_tf_idf(self, query: str, documents: List[Dict]) -> List[Tuple[str, float]]:
        """
        Calculate TF-IDF scores for query against document corpus.
        Returns: List of (doc_id, score) sorted by relevance.
        """
        if not documents:
            return []
        
        # Tokenize query
        query_terms = self._tokenize(query)
        
        # Calculate IDF for each term
        N = len(documents)
        idf_scores = {}
        for term in set(query_terms):
            df = sum(1 for doc in documents if term in self._tokenize(doc.get("search_text", "")))
            idf_scores[term] = math.log((N + 1) / (df + 1)) + 1
        
        # Calculate TF-IDF for each document
        scores = []
        for doc in documents:
            doc_text = self._tokenize(doc.get("search_text", ""))
            tf_idf = 0.0
            term_freq = Counter(doc_text)
            
            for term in query_terms:
                if term in term_freq:
                    tf = term_freq[term] / len(doc_text) if doc_text else 0
                    tf_idf += tf * idf_scores.get(term, 0)
            
            scores.append((doc.get("id"), tf_idf))
        
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple French text tokenization"""
        if not text:
            return []
        text = text.lower()
        # Remove special chars, keep French accents
        text = re.sub(r'[^\w\s\-\']', ' ', text)
        return [w for w in text.split() if len(w) > 2]
    
    def highlight_snippet(self, text: str, query: str, snippet_length: int = 200) -> str:
        """
        Extract a relevant snippet from text containing query terms.
        Returns highlighted snippet with <mark> tags.
        """
        if not text or not query:
            return text[:snippet_length] if text else ""
        
        query_terms = self._tokenize(query)
        text_lower = text.lower()
        
        # Find best position with most query terms
        best_pos = 0
        max_matches = 0
        words = text.split()
        
        for i in range(len(words)):
            window = " ".join(words[max(0, i-10):i+10]).lower()
            matches = sum(1 for term in query_terms if term in window)
            if matches > max_matches:
                max_matches = matches
                best_pos = max(0, i-10)
        
        # Extract snippet
        snippet_words = words[best_pos:best_pos+50]
        snippet = " ".join(snippet_words)
        
        # Highlight terms
        for term in query_terms:
            snippet = re.sub(f"({re.escape(term)})", r"<mark>\1</mark>", snippet, flags=re.IGNORECASE)
        
        return snippet[:snippet_length] + "..." if len(snippet) > snippet_length else snippet
    
    def rank_search_results(self, query: str, results: List[Dict], weights: Dict[str, float] = None) -> List[Dict]:
        """
        Rank search results by relevance.
        weights: {title: 3.0, keywords: 2.0, sections: 2.5, full_text: 1.0}
        """
        if weights is None:
            weights = {
                "title": 3.0,
                "keywords": 2.0,
                "sections": 2.5,
                "full_text": 1.0
            }
        
        query_terms = set(self._tokenize(query))
        
        for result in results:
            score = 0.0
            
            # Title match (high weight)
            title = self._tokenize(result.get("titre", ""))
            title_matches = len(query_terms.intersection(title))
            score += title_matches * weights["title"]
            
            # Keywords match
            keywords = [self._tokenize(k) for k in result.get("mots_cles", [])]
            keyword_matches = sum(1 for k in keywords if query_terms.intersection(k))
            score += keyword_matches * weights["keywords"]
            
            # Section match (problematic, solution, etc.)
            sections_text = " ".join([
                result.get("problematic", ""),
                result.get("solution", ""),
                result.get("resume", ""),
                result.get("summary", "")
            ])
            section_terms = self._tokenize(sections_text)
            section_matches = len(query_terms.intersection(section_terms))
            score += section_matches * weights["sections"]
            
            # Full text match (if available)
            full_text = self._tokenize(result.get("search_text", ""))
            full_matches = len(query_terms.intersection(full_text))
            score += full_matches * weights["full_text"]
            
            result["relevance_score"] = round(score, 2)
        
        return sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)
