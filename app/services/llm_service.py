import json
import re
from abc import ABC, abstractmethod
from typing import Any

import google.generativeai as genai
from openai import AsyncOpenAI
import httpx

from app.core.config import Settings
from app.core.exceptions import LLMServiceError
from app.schemas.restaurant import LLMAnalysisResult
from app.utils.constants import LLMProvider
from app.utils.prompts import RESTAURANT_ANALYSIS_PROMPT, OUTREACH_MESSAGE_PROMPT, COLLABORATION_SCORING_PROMPT

def _extract_json_from_text(text: str) -> dict[str, Any]:
    """Helper to extract JSON from LLM response strings which might include markdown code blocks."""
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = text.strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise LLMServiceError(f"Failed to parse JSON from LLM output: {e}. Output was: {text}")

class BaseLLMService(ABC):
    """Abstract Base Class for LLM Services."""
    
    @abstractmethod
    async def analyze_restaurant(self, restaurant_data: dict[str, Any], vision_data: dict[str, Any] | None) -> LLMAnalysisResult:
        """Analyze a restaurant using its data and vision data."""
        pass

    @abstractmethod
    async def generate_outreach(self, restaurant_data: dict[str, Any]) -> str:
        """Generate an outreach message for the restaurant."""
        pass

    @abstractmethod
    async def score_collaboration(self, restaurant_data: dict[str, Any]) -> dict[str, Any]:
        """Score collaboration potential and return JSON dictionary."""
        pass

class GeminiLLMService(BaseLLMService):
    """Gemini-based implementation of LLMService."""
    
    def __init__(self, settings: Settings) -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def analyze_restaurant(self, restaurant_data: dict[str, Any], vision_data: dict[str, Any] | None) -> LLMAnalysisResult:
        prompt = RESTAURANT_ANALYSIS_PROMPT.format(
            restaurant_data=json.dumps(restaurant_data, indent=2),
            vision_data=json.dumps(vision_data, indent=2) if vision_data else "None"
        )
        try:
            # We are using generate_content synchronously in async wrapper or assuming async generate_content_async
            # since google.generativeai provides generate_content_async
            response = await self.model.generate_content_async(prompt)
            parsed = _extract_json_from_text(response.text)
            return LLMAnalysisResult(**parsed)
        except Exception as e:
            raise LLMServiceError(f"Gemini analysis failed: {e}") from e

    async def generate_outreach(self, restaurant_data: dict[str, Any]) -> str:
        prompt = OUTREACH_MESSAGE_PROMPT.format(
            restaurant_data=json.dumps(restaurant_data, indent=2)
        )
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            raise LLMServiceError(f"Gemini outreach generation failed: {e}") from e

    async def score_collaboration(self, restaurant_data: dict[str, Any]) -> dict[str, Any]:
        prompt = COLLABORATION_SCORING_PROMPT.format(
            restaurant_data=json.dumps(restaurant_data, indent=2)
        )
        try:
            response = await self.model.generate_content_async(prompt)
            return _extract_json_from_text(response.text)
        except Exception as e:
            raise LLMServiceError(f"Gemini collaboration scoring failed: {e}") from e

class OpenAILLMService(BaseLLMService):
    """OpenAI-based implementation of LLMService."""
    
    def __init__(self, settings: Settings) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"

    async def analyze_restaurant(self, restaurant_data: dict[str, Any], vision_data: dict[str, Any] | None) -> LLMAnalysisResult:
        prompt = RESTAURANT_ANALYSIS_PROMPT.format(
            restaurant_data=json.dumps(restaurant_data, indent=2),
            vision_data=json.dumps(vision_data, indent=2) if vision_data else "None"
        )
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            text = response.choices[0].message.content or ""
            parsed = _extract_json_from_text(text)
            return LLMAnalysisResult(**parsed)
        except Exception as e:
            raise LLMServiceError(f"OpenAI analysis failed: {e}") from e

    async def generate_outreach(self, restaurant_data: dict[str, Any]) -> str:
        prompt = OUTREACH_MESSAGE_PROMPT.format(
            restaurant_data=json.dumps(restaurant_data, indent=2)
        )
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            raise LLMServiceError(f"OpenAI outreach generation failed: {e}") from e

    async def score_collaboration(self, restaurant_data: dict[str, Any]) -> dict[str, Any]:
        prompt = COLLABORATION_SCORING_PROMPT.format(
            restaurant_data=json.dumps(restaurant_data, indent=2)
        )
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            text = response.choices[0].message.content or ""
            return _extract_json_from_text(text)
        except Exception as e:
            raise LLMServiceError(f"OpenAI collaboration scoring failed: {e}") from e


def get_llm_service(settings: Settings) -> BaseLLMService:
    """Factory to return the configured LLMService."""
    if settings.LLM_PROVIDER.lower() == LLMProvider.OPENAI.value.lower():
        return OpenAILLMService(settings)
    return GeminiLLMService(settings)
