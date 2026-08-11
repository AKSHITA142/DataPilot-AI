import importlib
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

from backend.core.config import get_settings

import time
import threading

logger = logging.getLogger("datapilot.agents.base")
T = TypeVar("T", bound=BaseModel)

# Default timeout for LLM API calls (seconds)
_LLM_TIMEOUT_SECONDS = 30


class GeminiRateLimiter:
    """
    Enforces maximum 15 Requests Per Minute (RPM) for Google Gemini API calls.
    Maintains a minimum spacing of ~4.2 seconds between consecutive API calls to strictly abide by rate limits.
    """
    def __init__(self, max_rpm: int = 14):
        self.interval = 60.0 / max_rpm  # ~4.28s per call
        self.last_call_timestamp = 0.0
        self._lock = threading.Lock()

    def acquire(self):
        with self._lock:
            now = time.time()
            elapsed = now - self.last_call_timestamp
            if elapsed < self.interval:
                sleep_duration = self.interval - elapsed
                logger.info(f"Gemini Rate Limiter: Pausing {sleep_duration:.2f}s to enforce <15 RPM quota...")
                time.sleep(sleep_duration)
            self.last_call_timestamp = time.time()


_gemini_rate_limiter = GeminiRateLimiter(max_rpm=14)


def _clean_json_schema(schema: Any) -> Any:
    """Strips Google API unsupported keys from Pydantic JSON schema dicts for Gemini API compatibility."""
    FORBIDDEN_KEYS = {
        "additionalProperties",
        "$schema",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "minimum",
        "maximum",
    }
    if isinstance(schema, dict):
        return {
            k: _clean_json_schema(v)
            for k, v in schema.items()
            if k not in FORBIDDEN_KEYS
        }
    elif isinstance(schema, list):
        return [_clean_json_schema(item) for item in schema]
    return schema


class LLMClient:
    """Unified LLM client interface for reasoning agents supporting dynamic model choices."""

    def __init__(self, model_name: Optional[str] = None):
        settings = get_settings()
        self.model_name = model_name or settings.llm_model_name
        if not self.model_name:
            raise ValueError("LLM_MODEL_NAME is not set. Please define LLM_MODEL_NAME in your .env file.")
        self.gemini_key = settings.gemini_api_key
        self.openai_key = settings.openai_api_key
        self.timeout = _LLM_TIMEOUT_SECONDS



    def is_api_configured(self) -> bool:
        """Checks if a valid live API key is configured."""
        if self.gemini_key and not self.gemini_key.startswith("your_") and len(self.gemini_key) > 5:
            return True
        if self.openai_key and not self.openai_key.startswith("your_") and len(self.openai_key) > 5:
            return True
        return False

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        fallback_data: Dict[str, Any],
        system_instruction: Optional[str] = None,
    ) -> T:
        """Generates structured Pydantic response via live LLM or offline fallback."""
        if self.is_api_configured():
            try:
                logger.info(f"Invoking LLM model '{self.model_name}' for structured output {response_model.__name__}")
                
                # 1. Handle OpenAI if key configured
                if self.openai_key and not self.openai_key.startswith("your_"):
                    try:
                        openai_mod = importlib.import_module("openai")
                        client = openai_mod.OpenAI(api_key=self.openai_key)
                        resp = client.beta.chat.completions.parse(
                            model=self.model_name,
                            messages=[
                                {"role": "system", "content": system_instruction or "You are an expert AI Data Science assistant."},
                                {"role": "user", "content": prompt},
                            ],
                            response_format=response_model,
                        )
                        return resp.choices[0].message.parsed
                    except Exception as oe:
                        logger.warning(f"OpenAI call failed ({oe}); using fallback response")

                # 2. Handle Google Gemini if key configured
                elif self.gemini_key and not self.gemini_key.startswith("your_"):
                    try:
                        genai_mod = importlib.import_module("google.genai")
                        types_mod = importlib.import_module("google.genai.types")

                        # Enforce 15 RPM rate limiting before calling API
                        _gemini_rate_limiter.acquire()

                        # Create client with explicit HTTP timeout to prevent worker hangs
                        try:
                            client = genai_mod.Client(
                                api_key=self.gemini_key,
                                http_options={"timeout": self.timeout * 1000},  # ms
                            )
                        except Exception:
                            # Fallback: create client without explicit timeout config
                            client = genai_mod.Client(api_key=self.gemini_key)

                        # Clean JSON schema for Developer API compatibility
                        cleaned_schema = _clean_json_schema(response_model.model_json_schema())

                        logger.info(f"Calling Gemini model '{self.model_name}' (timeout={self.timeout}s)")
                        resp = client.models.generate_content(
                            model=self.model_name,
                            contents=prompt,
                            config=types_mod.GenerateContentConfig(
                                system_instruction=system_instruction or "You are an expert AI Data Science assistant.",
                                response_mime_type="application/json",
                                response_schema=cleaned_schema,
                            ),
                        )
                        return response_model.model_validate_json(resp.text)
                    except ImportError:
                        logger.error("google-genai package not installed. Run: pip install google-genai")
                    except TimeoutError:
                        logger.warning(f"Gemini API call timed out after {self.timeout}s; using fallback")
                    except Exception as ge:
                        logger.warning(f"Google GenAI SDK call failed ({type(ge).__name__}: {ge}); using fallback response")

            except Exception as exc:
                logger.warning(f"LLM API call failed ({exc}); using fallback response")

        # Deterministic offline fallback
        logger.info(f"Using rule-based fallback response for {response_model.__name__} (Model: {self.model_name})")
        return response_model.model_validate(fallback_data)


class BaseAgent(ABC):
    """Abstract base class for all DataPilot-AI reasoning agents."""

    def __init__(self, model_name: Optional[str] = None):
        self.llm_client = LLMClient(model_name=model_name)

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifier of the reasoning agent."""
        pass

    @property
    @abstractmethod
    def response_model(self) -> Type[BaseModel]:
        """Pydantic response model expected from this agent."""
        pass

    @abstractmethod
    def format_prompt(self, inputs: Dict[str, Any]) -> str:
        """Formats context variables into an LLM prompt string."""
        pass

    @abstractmethod
    def get_fallback_data(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Provides deterministic fallback data dictionary when offline."""
        pass

    def run(self, inputs: Dict[str, Any]) -> BaseModel:
        """Executes agent lifecycle: format prompt -> query LLM -> return validated model."""
        prompt = self.format_prompt(inputs)
        fallback = self.get_fallback_data(inputs)
        system_msg = f"You are the {self.name} in DataPilot-AI. Produce accurate structured JSON."
        return self.llm_client.generate_structured(
            prompt=prompt,
            response_model=self.response_model,
            fallback_data=fallback,
            system_instruction=system_msg,
        )
