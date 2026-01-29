"""
Hugging Face Inference API Client
Primary intelligence layer for CyberSentryAI
Provides unified interface for text, URL, image, and reasoning models
"""
import json
import os
import urllib.error
import urllib.request
from typing import Dict, Any, Optional, List
from datetime import datetime


class HuggingFaceClient:
    """
    Enterprise-grade Hugging Face Inference API client
    Handles primary AI intelligence with robust error handling
    """
    
    def __init__(self):
        """Initialize HF client with environment configuration"""
        # Load API configuration
        self.api_token = os.getenv("HF_API_TOKEN")
        self.timeout = float(os.getenv("HF_TIMEOUT", "15"))
        
        # Load model endpoints from environment
        self.text_model = os.getenv("HF_TEXT_MODEL", "mrm8488/bert-tiny-finetuned-sms-spam-detection")
        self.url_model = os.getenv("HF_URL_MODEL", "mrm8488/bert-tiny-finetuned-sms-spam-detection")
        self.image_model = os.getenv("HF_IMAGE_MODEL", "dima806/deepfake_vs_real_image_detection")
        self.redteam_model = os.getenv("HF_REDTEAM_MODEL", "HuggingFaceH4/zephyr-7b-beta")
        self.embedding_model = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        
        # Probability thresholds
        self.min_prob = float(os.getenv("HF_MIN_PROB", "0.25"))
        self.max_prob = float(os.getenv("HF_MAX_PROB", "0.45"))
        
        # Status tracking
        self._available = self.api_token is not None
        self._last_error = None
        self._last_call_time = None
    
    def is_available(self) -> bool:
        """Check if HF API is available and configured"""
        return self._available and self.api_token is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status for monitoring"""
        return {
            "available": self._available,
            "has_token": self.api_token is not None,
            "last_error": self._last_error,
            "last_call": self._last_call_time,
            "models": {
                "text": self.text_model,
                "url": self.url_model,
                "image": self.image_model,
                "redteam": self.redteam_model,
                "embedding": self.embedding_model
            }
        }
    
    def classify_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Classify text content for scam/spam detection
        
        Args:
            text: Text content to analyze
            
        Returns:
            Classification result or None on failure
            {
                "is_scam": bool,
                "confidence": float,
                "label": str,
                "model": str,
                "timestamp": str
            }
        """
        if not self.is_available():
            return None
        
        result = self._call_classification_api(
            model=self.text_model,
            inputs=text,
            task_type="text"
        )
        
        if result:
            # Normalize for scam detection using label + probability
            label = str(result.get("label", "")).lower()
            score = float(result.get("score", 0))
            is_scam = self._is_suspicious_label(label, score)
            
            return {
                "is_scam": is_scam,
                "confidence": score,
                "label": label,
                "model": self.text_model,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "huggingface"
            }
        
        return None
    
    def classify_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Classify URL for phishing detection
        
        Args:
            url: URL to analyze
            
        Returns:
            Classification result or None on failure
        """
        if not self.is_available():
            return None
        
        result = self._call_classification_api(
            model=self.url_model,
            inputs=url,
            task_type="url"
        )
        
        if result:
            label = str(result.get("label", "")).lower()
            score = float(result.get("score", 0))
            is_phishing = self._is_suspicious_label(label, score)
            
            return {
                "is_phishing": is_phishing,
                "confidence": score,
                "label": label,
                "model": self.url_model,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "huggingface"
            }
        
        return None
    
    def classify_image(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Classify image for deepfake/fake detection
        
        Args:
            image_data: Binary image data
            
        Returns:
            Classification result or None on failure
        """
        if not self.is_available():
            return None
        
        # For image classification, we need to send binary data
        result = self._call_image_api(
            model=self.image_model,
            image_data=image_data
        )
        
        if result:
            label = str(result.get("label", "")).lower()
            score = float(result.get("score", 0))
            is_fake = any(keyword in label for keyword in ["fake", "deepfake", "synthetic", "manipulated"])
            
            return {
                "is_fake": is_fake,
                "confidence": score,
                "label": label,
                "model": self.image_model,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "huggingface"
            }
        
        return None

    def _is_suspicious_label(self, label: str, score: float) -> bool:
        suspicious_threshold = self.min_prob
        malicious_threshold = self.max_prob

        risky_tokens = (
            "spam",
            "scam",
            "phishing",
            "malicious",
            "fraud",
            "social engineering",
            "unsafe",
            "threat",
            "negative",
        )
        safe_tokens = (
            "ham",
            "safe",
            "benign",
            "legit",
            "legitimate",
            "positive",
        )

        label_is_risky = any(token in label for token in risky_tokens)
        label_is_safe = any(token in label for token in safe_tokens)

        if label_is_safe and not label_is_risky:
            return False

        if label_is_risky:
            return score >= suspicious_threshold

        return score >= suspicious_threshold
    
    def generate_reasoning(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """
        Generate reasoning using red-team model
        
        Args:
            prompt: Reasoning prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None on failure
        """
        if not self.is_available():
            return None
        
        result = self._call_generation_api(
            model=self.redteam_model,
            prompt=prompt,
            max_tokens=max_tokens
        )
        
        return result
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding vector for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None on failure
        """
        if not self.is_available():
            return None
        
        # Truncate text if too long
        text = text[:500]
        
        api_url = f"https://api-inference.huggingface.co/models/{self.embedding_model}"
        payload = {
            "inputs": text,
            "options": {"wait_for_model": True}
        }
        
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            self._last_call_time = datetime.utcnow().isoformat()
            
            # Handle different response formats
            if isinstance(data, list):
                if isinstance(data[0], list):
                    return data[0]
                return data
            
            return None
            
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as e:
            self._last_error = f"Embedding error: {str(e)}"
            return None
    
    def _call_classification_api(
        self, 
        model: str, 
        inputs: str,
        task_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Call HF classification API
        
        Args:
            model: Model identifier
            inputs: Input text
            task_type: Type of task (text, url, image)
            
        Returns:
            Best classification result or None
        """
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        payload = {
            "inputs": inputs,
            "options": {"wait_for_model": True}
        }
        
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            self._last_call_time = datetime.utcnow().isoformat()
            self._last_error = None
            
            # Handle error responses
            if isinstance(data, dict) and "error" in data:
                self._last_error = f"API error: {data['error']}"
                return None
            
            # Handle nested list responses
            if isinstance(data, list) and data and isinstance(data[0], list):
                data = data[0]
            
            # Extract best classification
            if isinstance(data, list) and data:
                best = max(data, key=lambda item: item.get("score", 0))
                return {
                    "label": best.get("label", "unknown"),
                    "score": best.get("score", 0)
                }
            
            return None
            
        except urllib.error.HTTPError as e:
            self._last_error = f"HTTP {e.code}: {e.reason}"
            return None
        except urllib.error.URLError as e:
            self._last_error = f"Network error: {e.reason}"
            return None
        except TimeoutError:
            self._last_error = "Request timeout"
            return None
        except (ValueError, KeyError) as e:
            self._last_error = f"Parse error: {str(e)}"
            return None
    
    def _call_image_api(
        self, 
        model: str, 
        image_data: bytes
    ) -> Optional[Dict[str, Any]]:
        """
        Call HF image classification API
        
        Args:
            model: Model identifier
            image_data: Binary image data
            
        Returns:
            Best classification result or None
        """
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        req = urllib.request.Request(
            api_url,
            data=image_data,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/octet-stream",
            },
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            self._last_call_time = datetime.utcnow().isoformat()
            self._last_error = None
            
            # Handle error responses
            if isinstance(data, dict) and "error" in data:
                self._last_error = f"API error: {data['error']}"
                return None
            
            # Extract best classification
            if isinstance(data, list) and data:
                best = max(data, key=lambda item: item.get("score", 0))
                return {
                    "label": best.get("label", "unknown"),
                    "score": best.get("score", 0)
                }
            
            return None
            
        except urllib.error.HTTPError as e:
            self._last_error = f"HTTP {e.code}: {e.reason}"
            return None
        except urllib.error.URLError as e:
            self._last_error = f"Network error: {e.reason}"
            return None
        except TimeoutError:
            self._last_error = "Request timeout"
            return None
        except (ValueError, KeyError) as e:
            self._last_error = f"Parse error: {str(e)}"
            return None
    
    def _call_generation_api(
        self, 
        model: str, 
        prompt: str,
        max_tokens: int
    ) -> Optional[str]:
        """
        Call HF text generation API
        
        Args:
            model: Model identifier
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None
        """
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.3,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            
            self._last_call_time = datetime.utcnow().isoformat()
            self._last_error = None
            
            # Handle error responses
            if isinstance(data, dict) and "error" in data:
                self._last_error = f"API error: {data['error']}"
                return None
            
            # Extract generated text
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", "")
            elif isinstance(data, dict):
                return data.get("generated_text", "")
            
            return None
            
        except urllib.error.HTTPError as e:
            self._last_error = f"HTTP {e.code}: {e.reason}"
            return None
        except urllib.error.URLError as e:
            self._last_error = f"Network error: {e.reason}"
            return None
        except TimeoutError:
            self._last_error = "Request timeout"
            return None
        except (ValueError, KeyError) as e:
            self._last_error = f"Parse error: {str(e)}"
            return None


# Singleton instance for reuse across modules
_hf_client = None

def get_hf_client() -> HuggingFaceClient:
    """
    Get singleton HuggingFaceClient instance
    
    Returns:
        Shared HuggingFaceClient instance
    """
    global _hf_client
    if _hf_client is None:
        _hf_client = HuggingFaceClient()
    return _hf_client
