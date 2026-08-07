import base64
import httpx
from typing import Any

from app.core.config import Settings
from app.core.exceptions import GoogleVisionAPIError
from app.schemas.restaurant import VisionAnalysisResult
from app.utils.constants import VISION_MAX_RESULTS

class GoogleVisionService:
    """Service for interacting with Google Cloud Vision API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Google Vision Service with configuration settings."""
        self.api_key = settings.GOOGLE_VISION_API_KEY
        self.endpoint = "https://vision.googleapis.com/v1/images:annotate"

    async def analyze_photo(self, image_content: bytes) -> VisionAnalysisResult:
        """Analyze a photo and extract various features."""
        base64_image = base64.b64encode(image_content).decode("utf-8")
        
        payload = {
            "requests": [
                {
                    "image": {"content": base64_image},
                    "features": [
                        {"type": "LABEL_DETECTION", "maxResults": VISION_MAX_RESULTS},
                        {"type": "OBJECT_LOCALIZATION", "maxResults": VISION_MAX_RESULTS},
                        {"type": "TEXT_DETECTION"},
                        {"type": "LOGO_DETECTION", "maxResults": VISION_MAX_RESULTS},
                        {"type": "IMAGE_PROPERTIES", "maxResults": VISION_MAX_RESULTS},
                        {"type": "SAFE_SEARCH_DETECTION"}
                    ]
                }
            ]
        }
        
        params = {"key": self.api_key}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.endpoint, params=params, json=payload, timeout=20.0)
                response.raise_for_status()
                data = response.json()
                
                if "responses" not in data or not data["responses"]:
                    raise GoogleVisionAPIError("No response received from Vision API.")
                
                result_data = data["responses"][0]
                if "error" in result_data:
                    raise GoogleVisionAPIError(f"Vision API Error: {result_data['error'].get('message', 'Unknown error')}")
                
                return VisionAnalysisResult(
                    labels=self._parse_labels(result_data),
                    objects=self._parse_objects(result_data),
                    text=self._parse_text(result_data),
                    logos=self._parse_logos(result_data),
                    dominant_colors=self._parse_colors(result_data),
                    safe_search=self._parse_safe_search(result_data)
                )
            except httpx.RequestError as e:
                raise GoogleVisionAPIError(f"Network error during Vision API call: {e}") from e

    def _parse_labels(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract label annotations."""
        labels = response.get("labelAnnotations", [])
        return [{"description": l.get("description"), "score": l.get("score")} for l in labels]

    def _parse_objects(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract localized object annotations."""
        objects = response.get("localizedObjectAnnotations", [])
        return [{"name": o.get("name"), "score": o.get("score")} for o in objects]

    def _parse_text(self, response: dict[str, Any]) -> list[str]:
        """Extract text annotations."""
        text_annotations = response.get("textAnnotations", [])
        return [t.get("description") for t in text_annotations] if text_annotations else []

    def _parse_logos(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract logo annotations."""
        logos = response.get("logoAnnotations", [])
        return [{"description": l.get("description"), "score": l.get("score")} for l in logos]

    def _parse_colors(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract dominant colors from image properties."""
        props = response.get("imagePropertiesAnnotation", {})
        colors = props.get("dominantColors", {}).get("colors", [])
        return [{"color": c.get("color"), "score": c.get("score")} for c in colors]

    def _parse_safe_search(self, response: dict[str, Any]) -> dict[str, str]:
        """Extract safe search annotation."""
        return response.get("safeSearchAnnotation", {})
