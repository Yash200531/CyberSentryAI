"""
Performance optimizations for CyberSentryAI
Async operations, caching, batch processing
"""
import asyncio
import aiohttp
import hashlib
import json
import time
from typing import Dict, Any, List, Optional
from functools import lru_cache
from datetime import datetime, timedelta


class AsyncHFClient:
    """
    Async Hugging Face API client with caching and rate limiting
    """
    
    def __init__(self, api_token: str, cache_ttl: int = 300):
        self.api_token = api_token
        self.cache_ttl = cache_ttl  # seconds
        self._cache = {}
        self._cache_timestamps = {}
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def classify_text_async(self, model_url: str, text: str) -> Optional[Dict]:
        """Async text classification with caching"""
        cache_key = self._get_cache_key(model_url, text)
        
        # Check cache
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        # Call API
        payload = {"inputs": text}
        result = await self._call_api(model_url, payload)
        
        # Cache result
        if result:
            self._cache[cache_key] = result
            self._cache_timestamps[cache_key] = time.time()
        
        return result
    
    async def classify_image_async(self, model_url: str, image_bytes: bytes) -> Optional[Dict]:
        """Async image classification"""
        cache_key = self._get_cache_key(model_url, image_bytes[:100])  # Cache based on first 100 bytes
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        result = await self._call_api(model_url, image_bytes, is_binary=True)
        
        if result:
            self._cache[cache_key] = result
            self._cache_timestamps[cache_key] = time.time()
        
        return result
    
    async def get_embedding_async(self, model_url: str, text: str) -> Optional[List[float]]:
        """Async embedding generation with caching"""
        cache_key = self._get_cache_key(model_url, text)
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        payload = {"inputs": text, "options": {"wait_for_model": True}}
        result = await self._call_api(model_url, payload)
        
        # Extract embedding
        if result:
            if isinstance(result, list) and len(result) > 0:
                embedding = result[0] if isinstance(result[0], list) else result
                self._cache[cache_key] = embedding
                self._cache_timestamps[cache_key] = time.time()
                return embedding
        
        return None
    
    async def batch_classify_text(self, model_url: str, texts: List[str]) -> List[Optional[Dict]]:
        """Batch text classification for efficiency"""
        tasks = [self.classify_text_async(model_url, text) for text in texts]
        return await asyncio.gather(*tasks)
    
    async def batch_embeddings(self, model_url: str, texts: List[str]) -> List[Optional[List[float]]]:
        """Batch embedding generation"""
        tasks = [self.get_embedding_async(model_url, text) for text in texts]
        return await asyncio.gather(*tasks)
    
    async def _call_api(self, url: str, payload: Any, is_binary: bool = False) -> Optional[Any]:
        """Internal async API call"""
        headers = {
            "Authorization": f"Bearer {self.api_token}",
        }
        
        if is_binary:
            headers["Content-Type"] = "application/octet-stream"
            data = payload
        else:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload)
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, data=data, headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result
                    else:
                        return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Async API error: {e}")
            return None
    
    def _get_cache_key(self, url: str, content: Any) -> str:
        """Generate cache key"""
        if isinstance(content, bytes):
            content_hash = hashlib.md5(content).hexdigest()
        else:
            content_hash = hashlib.md5(str(content).encode()).hexdigest()
        return f"{url}:{content_hash}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is valid"""
        if cache_key not in self._cache:
            return False
        
        timestamp = self._cache_timestamps.get(cache_key, 0)
        age = time.time() - timestamp
        
        return age < self.cache_ttl
    
    def clear_cache(self):
        """Clear all cached entries"""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    def clear_old_cache(self):
        """Clear expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if current_time - timestamp > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
            del self._cache_timestamps[key]


class OptimizedRedTeamEngine:
    """
    Optimized Red-Team engine with async support
    """
    
    def __init__(self, async_client: AsyncHFClient):
        self.async_client = async_client
        self.model_url = f"https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    
    async def analyze_async(
        self, 
        content: str, 
        content_type: str, 
        scan_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Async red-team analysis"""
        is_threat = (
            scan_result.get("is_scam") or 
            scan_result.get("is_phishing") or 
            scan_result.get("is_fake", False)
        )
        
        if not is_threat or scan_result.get("score", 0) * 100 < 50:
            return self._minimal_analysis()
        
        # Build prompt based on type
        prompt = self._build_prompt(content, content_type, scan_result)
        
        # Call API async
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.3,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        result = await self.async_client._call_api(self.model_url, payload)
        
        if result and isinstance(result, list) and len(result) > 0:
            response = result[0].get("generated_text", "")
            parsed = self._parse_response(response)
            parsed["timestamp"] = datetime.utcnow().isoformat()
            return parsed
        
        return self._minimal_analysis()
    
    def _build_prompt(self, content: str, content_type: str, scan_result: Dict) -> str:
        """Build analysis prompt"""
        confidence = scan_result.get("score", 0) * 100
        
        if content_type == "url":
            return f"""Analyze this suspicious URL (confidence: {confidence:.0f}%). Provide JSON with: attack_goal, victim_profile, psychological_tactics, exploitation_chain, next_step, severity (1-10), confidence_score (0-100).

URL: {content}

JSON:"""
        else:
            return f"""Analyze this suspicious message (confidence: {confidence:.0f}%). Provide JSON with: attack_goal, victim_profile, psychological_tactics, exploitation_chain, next_step, severity (1-10), confidence_score (0-100).

Message: "{content[:500]}"

JSON:"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                parsed = json.loads(response[start:end])
                return {
                    "attack_goal": str(parsed.get("attack_goal", "Unknown"))[:200],
                    "victim_profile": str(parsed.get("victim_profile", "General users"))[:200],
                    "psychological_tactics": parsed.get("psychological_tactics", [])[:5],
                    "exploitation_chain": str(parsed.get("exploitation_chain", ""))[:500],
                    "next_step": str(parsed.get("next_step", "Unknown"))[:200],
                    "severity": max(1, min(10, int(parsed.get("severity", 5)))),
                    "confidence_score": max(0, min(100, float(parsed.get("confidence_score", 50))))
                }
        except (json.JSONDecodeError, ValueError, KeyError):
            pass
        
        return self._minimal_analysis()
    
    def _minimal_analysis(self) -> Dict[str, Any]:
        """Minimal analysis"""
        return {
            "attack_goal": "None detected",
            "victim_profile": "N/A",
            "psychological_tactics": [],
            "exploitation_chain": "No significant threat detected",
            "next_step": "N/A",
            "severity": 1,
            "confidence_score": 0,
            "timestamp": datetime.utcnow().isoformat()
        }


class OptimizedDNAEngine:
    """
    Optimized Cyber DNA engine with async embeddings
    """
    
    def __init__(self, async_client: AsyncHFClient):
        self.async_client = async_client
        self.model_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    
    async def generate_dna_async(
        self,
        content: str,
        content_type: str,
        scan_result: Dict[str, Any],
        redteam_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Async DNA generation"""
        
        # Extract features (sync operations)
        linguistic_score = self._extract_linguistic_score(content)
        urgency_score = self._extract_urgency_score(content)
        brand_score = self._extract_brand_impersonation_score(content)
        obfuscation_score = self._extract_obfuscation_score(content, content_type)
        visual_score = self._extract_visual_deception_score(content_type, scan_result)
        intent_score = self._calculate_intent_severity(scan_result, redteam_result)
        
        # Get embedding async
        embedding = await self.async_client.get_embedding_async(self.model_url, content[:500])
        
        # Generate DNA hash
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
            "embedding_vector": embedding[:50] if embedding else None,
            "embedding_full": embedding,
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "timestamp": datetime.utcnow().isoformat(),
            "overall_threat_score": round(self._calculate_overall_score(
                linguistic_score, urgency_score, brand_score,
                obfuscation_score, visual_score, intent_score
            ), 2)
        }
    
    # Feature extraction methods (same as original, omitted for brevity)
    def _extract_linguistic_score(self, content: str) -> float:
        if not content:
            return 0.0
        content_lower = content.lower()
        score = 0.0
        power_words = ["urgent", "immediate", "verify", "suspended", "prize", "free"]
        matches = sum(1 for word in power_words if word in content_lower)
        score += min(50, matches * 8)
        return min(100.0, score)
    
    def _extract_urgency_score(self, content: str) -> float:
        if not content:
            return 0.0
        content_lower = content.lower()
        urgency_phrases = ["urgent", "immediately", "expire", "last chance"]
        matches = sum(1 for phrase in urgency_phrases if phrase in content_lower)
        return min(100, matches * 15)
    
    def _extract_brand_impersonation_score(self, content: str) -> float:
        if not content:
            return 0.0
        content_lower = content.lower()
        brands = ["paypal", "amazon", "bank", "microsoft"]
        matches = sum(1 for brand in brands if brand in content_lower)
        return min(100, 40 + (matches * 20)) if matches > 0 else 0
    
    def _extract_obfuscation_score(self, content: str, content_type: str) -> float:
        if not content:
            return 0.0
        score = 0.0
        if content_type == "url":
            if "@" in content:
                score += 25
            if content.count("-") > 3:
                score += 20
        return min(100.0, score)
    
    def _extract_visual_deception_score(self, content_type: str, scan_result: Dict) -> float:
        if content_type == "image":
            is_fake = scan_result.get("is_fake", False)
            confidence = scan_result.get("score", 0) * 100
            return confidence if is_fake else 0.0
        return 0.0
    
    def _calculate_intent_severity(self, scan_result: Dict, redteam_result: Optional[Dict]) -> float:
        is_threat = (
            scan_result.get("is_scam") or
            scan_result.get("is_phishing") or
            scan_result.get("is_fake", False)
        )
        if not is_threat:
            return 0.0
        confidence = scan_result.get("score", 0) * 100
        if redteam_result:
            severity = redteam_result.get("severity", 5)
            severity_boost = (severity / 10) * 30
            return min(100, confidence + severity_boost)
        return confidence
    
    def _calculate_overall_score(self, l, u, b, o, v, i) -> float:
        return (l * 0.15 + u * 0.15 + b * 0.20 + o * 0.15 + v * 0.15 + i * 0.20)
    
    def _generate_dna_hash(self, l, u, b, o, v, i) -> str:
        fingerprint = f"{l:.2f}|{u:.2f}|{b:.2f}|{o:.2f}|{v:.2f}|{i:.2f}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]


# Global client instance
_async_client = None

def get_async_client(api_token: str) -> AsyncHFClient:
    """Get or create global async client"""
    global _async_client
    if _async_client is None:
        _async_client = AsyncHFClient(api_token, cache_ttl=300)
    return _async_client
