"""
Shared Hugging Face Inference API client helpers.
"""

import logging
import requests

logger = logging.getLogger(__name__)


class HuggingFaceInferenceClient:
    """Minimal client for Hugging Face Inference API (server-side)."""

    def __init__(self, token: str, timeout_s: int = 60):
        self.token = token or ""
        self.timeout_s = timeout_s

    def _headers(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def post_json(self, model: str, payload: dict):
        # Try multiple endpoint formats for compatibility
        endpoints = [
            f"https://api-inference.huggingface.co/models/{model}",
            f"https://router.huggingface.co/hf-inference/models/{model}",
            f"https://router.huggingface.co/models/{model}"
        ]
        
        last_error = None
        for url in endpoints:
            try:
                resp = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout_s)
                if resp.status_code != 410:  # Skip deprecated endpoints
                    resp.raise_for_status()
                    return resp
            except requests.exceptions.HTTPError as e:
                if resp.status_code == 410:
                    logger.warning(f"Endpoint {url} is deprecated (410), trying next...")
                    continue
                last_error = e
            except Exception as e:
                last_error = e
                continue
        
        # If all endpoints failed, raise the last error
        if last_error:
            raise last_error
        raise requests.exceptions.HTTPError("All Hugging Face endpoints failed")

    def post_binary(self, model: str, data: bytes, content_type: str = "application/octet-stream"):
        # Try multiple endpoint formats for compatibility
        endpoints = [
            f"https://api-inference.huggingface.co/models/{model}",
            f"https://router.huggingface.co/hf-inference/models/{model}",
            f"https://router.huggingface.co/models/{model}"
        ]
        
        headers = self._headers()
        headers["Content-Type"] = content_type
        
        last_error = None
        for url in endpoints:
            try:
                resp = requests.post(url, headers=headers, data=data, timeout=self.timeout_s)
                if resp.status_code != 410:  # Skip deprecated endpoints
                    resp.raise_for_status()
                    return resp
            except requests.exceptions.HTTPError as e:
                if resp.status_code == 410:
                    logger.warning(f"Endpoint {url} is deprecated (410), trying next...")
                    continue
                last_error = e
            except Exception as e:
                last_error = e
                continue
        
        # If all endpoints failed, raise the last error
        if last_error:
            raise last_error
        raise requests.exceptions.HTTPError("All Hugging Face endpoints failed")

