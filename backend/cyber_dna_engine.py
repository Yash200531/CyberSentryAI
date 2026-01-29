"""
Cyber DNA Fingerprinting Engine
Creates unique fingerprints for scam/phishing content
Uses embeddings and feature extraction for similarity detection
"""
import json
import os
import urllib.error
import urllib.request
import numpy as np
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib


class CyberDNAEngine:
    """
    Generates Cyber DNA fingerprints for threats
    Enables similarity matching and lineage detection
    """
    
    def __init__(self):
        self.api_token = os.getenv("HF_API_TOKEN")
        # Fast, lightweight embedding model
        self.embedding_model = os.getenv(
            "HF_EMBEDDING_MODEL", 
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.api_url = f"https://api-inference.huggingface.co/models/{self.embedding_model}"
        self.timeout = float(os.getenv("HF_TIMEOUT", "15"))
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
        # Cache for embeddings (in production, use Redis)
        self._embedding_cache = {}
        
    def generate_dna(
        self, 
        content: str, 
        content_type: str,
        scan_result: Dict[str, Any],
        redteam_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete Cyber DNA fingerprint
        
        Args:
            content: Raw text/URL content
            content_type: 'text', 'url', 'image'
            scan_result: Primary detection results
            redteam_result: Optional red-team analysis
            
        Returns:
            Complete Cyber DNA with scores and embedding
        """
        # Extract linguistic features
        linguistic_score = self._extract_linguistic_score(content)
        
        # Extract urgency/pressure
        urgency_score = self._extract_urgency_score(content)
        
        # Extract brand impersonation
        brand_score = self._extract_brand_impersonation_score(content)
        
        # Extract obfuscation
        obfuscation_score = self._extract_obfuscation_score(content, content_type)
        
        # Visual deception (for images or URLs with visual elements)
        visual_score = self._extract_visual_deception_score(content_type, scan_result)
        
        # Intent severity from scan and redteam
        intent_score = self._calculate_intent_severity(scan_result, redteam_result)
        
        # Generate embedding vector
        embedding = self._get_embedding(content)
        
        # Create unique DNA hash
        dna_hash = self._generate_dna_hash(
            linguistic_score, urgency_score, brand_score, 
            obfuscation_score, visual_score, intent_score
        )
        
        return {
            "dna_hash": dna_hash,
            "content_type": content_type,
            "scores": {
                "linguistic_manipulation": round(linguistic_score, 2),
                "urgency_pressure": round(urgency_score, 2),
                "brand_impersonation": round(brand_score, 2),
                "obfuscation": round(obfuscation_score, 2),
                "visual_deception": round(visual_score, 2),
                "intent_severity": round(intent_score, 2)
            },
            "embedding_vector": embedding[:50] if embedding else None,  # Store first 50 dims for logs
            "embedding_full": embedding,  # Full vector for similarity
            "embedding_model": self.embedding_model,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_threat_score": round(self._calculate_overall_score(
                linguistic_score, urgency_score, brand_score, 
                obfuscation_score, visual_score, intent_score
            ), 2)
        }
    
    def calculate_similarity(
        self, 
        dna1: Dict[str, Any], 
        dna2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate similarity between two Cyber DNA fingerprints
        
        Args:
            dna1: First DNA fingerprint
            dna2: Second DNA fingerprint
            
        Returns:
            Similarity metrics and same-actor probability
        """
        # Embedding similarity (cosine)
        emb1 = dna1.get("embedding_full")
        emb2 = dna2.get("embedding_full")
        
        if emb1 and emb2 and len(emb1) == len(emb2):
            embedding_similarity = self._cosine_similarity(emb1, emb2)
        else:
            embedding_similarity = 0.0
        
        # Feature vector similarity
        scores1 = dna1.get("scores", {})
        scores2 = dna2.get("scores", {})
        
        feature_similarity = self._feature_similarity(scores1, scores2)
        
        # Combined similarity
        combined_similarity = (embedding_similarity * 0.7) + (feature_similarity * 0.3)
        
        # Same actor probability
        same_actor_probability = self._calculate_same_actor_probability(
            embedding_similarity, feature_similarity
        )
        
        return {
            "embedding_similarity": round(embedding_similarity * 100, 2),
            "feature_similarity": round(feature_similarity * 100, 2),
            "combined_similarity": round(combined_similarity * 100, 2),
            "same_actor_probability": round(same_actor_probability, 2),
            "lineage_detected": combined_similarity > 0.75,
            "confidence": round(min(embedding_similarity, feature_similarity) * 100, 2)
        }
    
    def find_similar_threats(
        self, 
        target_dna: Dict[str, Any], 
        dna_database: List[Dict[str, Any]],
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find similar threats in database
        
        Args:
            target_dna: Target DNA to match
            dna_database: List of historical DNA fingerprints
            threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of similar threats with similarity scores
        """
        similar = []
        
        for db_dna in dna_database:
            similarity = self.calculate_similarity(target_dna, db_dna)
            
            if similarity["combined_similarity"] / 100 >= threshold:
                similar.append({
                    "dna_hash": db_dna.get("dna_hash"),
                    "timestamp": db_dna.get("timestamp"),
                    "similarity": similarity,
                    "threat_score": db_dna.get("overall_threat_score")
                })
        
        # Sort by similarity
        similar.sort(key=lambda x: x["similarity"]["combined_similarity"], reverse=True)
        
        return similar
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding vector from Hugging Face"""
        if not self.api_token or not text:
            return None
        
        # Check cache
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self._embedding_cache:
            return self._embedding_cache[text_hash]
        
        # Truncate text if too long
        text = text[:500]
        
        payload = {
            "inputs": text,
            "options": {"wait_for_model": True}
        }
        
        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            # Handle different response formats
            if isinstance(data, list) and len(data) > 0:
                embedding = data[0] if isinstance(data[0], list) else data
            elif isinstance(data, dict) and "error" not in data:
                embedding = data.get("embeddings", [])
            else:
                return None
            
            # Cache the result
            if len(embedding) == self.embedding_dim:
                self._embedding_cache[text_hash] = embedding
                return embedding
                
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as e:
            print(f"Embedding API Error: {e}")
            return None
        
        return None
    
    def _extract_linguistic_score(self, content: str) -> float:
        """
        Calculate linguistic manipulation score (0-100)
        Based on persuasion patterns, power words, manipulation tactics
        """
        if not content:
            return 0.0
        
        content_lower = content.lower()
        score = 0.0
        
        # Power words / manipulation triggers
        power_words = [
            "urgent", "immediate", "act now", "limited time", "expire",
            "verify", "confirm", "suspended", "locked", "unauthorized",
            "winner", "congratulations", "selected", "prize", "free",
            "guarantee", "risk-free", "no obligation", "click here",
            "important", "alert", "warning", "security", "account"
        ]
        
        matches = sum(1 for word in power_words if word in content_lower)
        score += min(50, matches * 8)
        
        # Excessive punctuation
        exclamation_count = content.count("!")
        question_count = content.count("?")
        if exclamation_count > 2 or question_count > 3:
            score += 15
        
        # ALL CAPS detection
        words = content.split()
        caps_words = sum(1 for word in words if word.isupper() and len(word) > 3)
        if caps_words > 0:
            score += min(20, caps_words * 5)
        
        # Urgency indicators
        if any(phrase in content_lower for phrase in ["within 24", "expire", "last chance"]):
            score += 15
        
        return min(100.0, score)
    
    def _extract_urgency_score(self, content: str) -> float:
        """Calculate urgency/pressure score (0-100)"""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        score = 0.0
        
        urgency_phrases = [
            "urgent", "immediately", "asap", "right now", "act now",
            "expire", "expires", "expiring", "deadline", "limited time",
            "hurry", "quick", "quickly", "fast", "today only",
            "last chance", "final notice", "time sensitive"
        ]
        
        matches = sum(1 for phrase in urgency_phrases if phrase in content_lower)
        score = min(100, matches * 15)
        
        return score
    
    def _extract_brand_impersonation_score(self, content: str) -> float:
        """Calculate brand impersonation score (0-100)"""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        score = 0.0
        
        # Common impersonated brands
        brands = [
            "paypal", "amazon", "microsoft", "apple", "google",
            "facebook", "instagram", "netflix", "bank", "fedex",
            "dhl", "ups", "irs", "social security", "government",
            "chase", "wells fargo", "citibank", "visa", "mastercard"
        ]
        
        matches = sum(1 for brand in brands if brand in content_lower)
        if matches > 0:
            score = min(100, 40 + (matches * 20))
        
        # Generic authority claims
        authority_words = ["official", "authorized", "verified", "certified"]
        authority_matches = sum(1 for word in authority_words if word in content_lower)
        score += min(30, authority_matches * 10)
        
        return min(100.0, score)
    
    def _extract_obfuscation_score(self, content: str, content_type: str) -> float:
        """Calculate obfuscation/evasion score (0-100)"""
        if not content:
            return 0.0
        
        score = 0.0
        
        if content_type == "url":
            # URL obfuscation
            if "@" in content:
                score += 25
            if content.count("-") > 3:
                score += 20
            if content.count(".") > 4:
                score += 15
            if any(char in content for char in ["%", "~", ";"]):
                score += 20
            if not content.startswith("https"):
                score += 20
        else:
            # Text obfuscation
            # Zero-width characters, excessive spacing
            if "  " in content:
                score += 15
            
            # Mixed character sets
            if re.search(r'[а-я]', content):  # Cyrillic lookalikes
                score += 30
            
            # URL shorteners
            if any(short in content.lower() for short in ["bit.ly", "tinyurl", "goo.gl"]):
                score += 25
            
            # Encoded content
            if re.search(r'%[0-9A-Fa-f]{2}', content):
                score += 20
        
        return min(100.0, score)
    
    def _extract_visual_deception_score(
        self, 
        content_type: str, 
        scan_result: Dict[str, Any]
    ) -> float:
        """Calculate visual deception score (0-100)"""
        if content_type == "image":
            # Based on image detection confidence
            is_fake = scan_result.get("is_fake", False)
            confidence = scan_result.get("score", 0) * 100
            
            if is_fake:
                return confidence
            else:
                return 0.0
        else:
            # For text/URL, look for visual mimicry indicators
            return 0.0
    
    def _calculate_intent_severity(
        self, 
        scan_result: Dict[str, Any],
        redteam_result: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate overall intent severity (0-100)"""
        # Base severity from scan
        is_threat = (
            scan_result.get("is_scam") or 
            scan_result.get("is_phishing") or 
            scan_result.get("is_fake", False)
        )
        
        if not is_threat:
            return 0.0
        
        confidence = scan_result.get("score", 0) * 100
        
        # Enhance with red-team analysis
        if redteam_result:
            severity = redteam_result.get("severity", 5)
            # Map 1-10 to contribution factor
            severity_boost = (severity / 10) * 30
            return min(100, confidence + severity_boost)
        
        return confidence
    
    def _calculate_overall_score(
        self, 
        linguistic: float, 
        urgency: float, 
        brand: float,
        obfuscation: float, 
        visual: float, 
        intent: float
    ) -> float:
        """Calculate weighted overall threat score (0-100)"""
        # Weighted combination
        weights = {
            "linguistic": 0.15,
            "urgency": 0.15,
            "brand": 0.20,
            "obfuscation": 0.15,
            "visual": 0.15,
            "intent": 0.20
        }
        
        overall = (
            linguistic * weights["linguistic"] +
            urgency * weights["urgency"] +
            brand * weights["brand"] +
            obfuscation * weights["obfuscation"] +
            visual * weights["visual"] +
            intent * weights["intent"]
        )
        
        return overall
    
    def _generate_dna_hash(
        self, 
        linguistic: float, 
        urgency: float, 
        brand: float,
        obfuscation: float, 
        visual: float, 
        intent: float
    ) -> str:
        """Generate unique DNA hash from feature scores"""
        # Create fingerprint string
        fingerprint = f"{linguistic:.2f}|{urgency:.2f}|{brand:.2f}|{obfuscation:.2f}|{visual:.2f}|{intent:.2f}"
        
        # Generate hash
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        # Convert to numpy for efficient computation
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def _feature_similarity(self, scores1: Dict, scores2: Dict) -> float:
        """Calculate similarity between feature score vectors"""
        if not scores1 or not scores2:
            return 0.0
        
        # Extract score vectors
        keys = ["linguistic_manipulation", "urgency_pressure", "brand_impersonation",
                "obfuscation", "visual_deception", "intent_severity"]
        
        vec1 = [scores1.get(k, 0) for k in keys]
        vec2 = [scores2.get(k, 0) for k in keys]
        
        return self._cosine_similarity(vec1, vec2)
    
    def _calculate_same_actor_probability(
        self, 
        embedding_sim: float, 
        feature_sim: float
    ) -> float:
        """
        Calculate probability that two threats are from the same actor
        Returns 0-100
        """
        # High similarity in both dimensions suggests same actor
        if embedding_sim > 0.85 and feature_sim > 0.85:
            return 95.0
        elif embedding_sim > 0.75 and feature_sim > 0.75:
            return 80.0
        elif embedding_sim > 0.65 and feature_sim > 0.65:
            return 65.0
        elif embedding_sim > 0.5 and feature_sim > 0.5:
            return 45.0
        else:
            return max(0, (embedding_sim + feature_sim) / 2 * 100)
