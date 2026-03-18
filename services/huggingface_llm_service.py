"""
Hugging Face LLM Service (text generation).

Uses Hugging Face Inference API for answering (e.g., mistralai/Mistral-7B-Instruct-v0.3).
"""

import logging

from services.huggingface_client import HuggingFaceInferenceClient

logger = logging.getLogger(__name__)


class HuggingFaceLLMService:
    """LLM via Hugging Face Inference API."""

    def __init__(self, token=None, model=None, max_tokens=None, temperature=None):
        from config import Config

        self.token = token or Config.HUGGINGFACE_TOKEN
        self.model = model or Config.HF_LLM_MODEL or "mistralai/Mistral-7B-Instruct-v0.3"
        self.max_tokens = int(max_tokens or Config.HF_LLM_MAX_TOKENS or 200)
        self.temperature = float(temperature or Config.HF_LLM_TEMPERATURE or 0.7)
        self.client = HuggingFaceInferenceClient(self.token, timeout_s=60)

        if not self.token:
            logger.warning("HUGGINGFACE_TOKEN not found. HuggingFace LLM may be rate-limited or unavailable.")

        # Keep it voice-friendly.
        self.system_prompt = """You are a helpful and professional voice assistant for a call center.
You are speaking to customers over the phone in a natural, conversational way.
Keep responses concise (2-3 sentences max) and ask a follow-up question when helpful."""

        logger.info(f"HuggingFace LLM initialized with model: {self.model}")

    def _build_prompt(self, user_input, conversation_history=None):
        # Minimal, broadly compatible prompt (works even if model isn't chat-templated server-side).
        prompt = self.system_prompt.strip() + "\n\n"
        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "assistant":
                    prompt += f"Assistant: {content}\n"
                else:
                    prompt += f"User: {content}\n"
        prompt += f"User: {user_input}\nAssistant:"
        return prompt

    def generate_response(self, user_input, call_id=None, conversation_history=None):
        if not user_input:
            return "Sorry—could you repeat that?"

        try:
            prompt = self._build_prompt(user_input, conversation_history=conversation_history)

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "return_full_text": False,
                },
            }

            resp = self.client.post_json(self.model, payload)
            data = resp.json()

            text = None
            if isinstance(data, list) and data and isinstance(data[0], dict):
                text = data[0].get("generated_text")
            elif isinstance(data, dict):
                text = data.get("generated_text") or data.get("text")

            if not text:
                logger.error(f"Unexpected LLM response format: {data}")
                return "I’m sorry—I’m having trouble answering that right now. Could you try again?"

            answer = str(text).strip()
            logger.info(f"Generated HF response for call {call_id}: {answer[:100]}...")
            return answer

        except Exception as e:
            logger.error(f"Error generating HF LLM response: {str(e)}", exc_info=True)
            return "I’m sorry—I’m having trouble answering that right now. Could you try again?"

