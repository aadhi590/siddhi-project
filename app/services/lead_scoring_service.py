from typing import Any

class LeadScoringService:
    """Service for calculating automated lead scores for restaurants."""

    def __init__(self) -> None:
        """Initialize LeadScoringService."""
        pass

    def calculate_premium_score(self, restaurant_data: dict[str, Any], vision_data: dict[str, Any] | None = None) -> float:
        """
        Calculate a premium score (0-100).
        Weights:
        - Rating (30%)
        - Price Level (25%)
        - Review Count (20%)
        - Photo Quality (15%)
        - Website Presence (10%)
        """
        rating_score = self._rating_score(restaurant_data.get("rating"))
        price_score = self._price_level_score(restaurant_data.get("price_level"))
        review_score = self._review_count_score(restaurant_data.get("user_rating_count") or restaurant_data.get("user_ratings_total"))
        photo_score = self._photo_quality_score(vision_data)
        web_score = self._website_score(restaurant_data.get("website"))

        total_score = (
            (rating_score * 0.30) +
            (price_score * 0.25) +
            (review_score * 0.20) +
            (photo_score * 0.15) +
            (web_score * 0.10)
        )
        return round(total_score, 2)

    def calculate_collaboration_score(self, restaurant_data: dict[str, Any], ai_analysis: dict[str, Any] | None = None) -> float:
        """
        Calculate a collaboration score (0-100).
        Weights:
        - Premium Score (30%)
        - Audience Match (25%)
        - Marketing Potential (25%)
        - Online Presence (20%)
        """
        premium = restaurant_data.get("premium_score", 0)
        
        target_audience = ai_analysis.get("target_audience") if ai_analysis else None
        audience_score = self._audience_match_score(target_audience)
        
        marketing_score = self._marketing_potential_score(ai_analysis)
        presence_score = self._online_presence_score(restaurant_data)

        total_score = (
            (premium * 0.30) +
            (audience_score * 0.25) +
            (marketing_score * 0.25) +
            (presence_score * 0.20)
        )
        return round(total_score, 2)

    def _rating_score(self, rating: float | None) -> float:
        """Score based on user rating. Assume max 5.0."""
        if not rating:
            return 0.0
        return min(max((rating / 5.0) * 100, 0.0), 100.0)

    def _price_level_score(self, price_level: int | None) -> float:
        """Score based on price level (typically 0-4)."""
        if price_level is None:
            return 25.0  # Default moderate score
        return min(max((price_level / 4.0) * 100, 0.0), 100.0)

    def _review_count_score(self, count: int | None) -> float:
        """Score based on review count (logarithmic curve maxing at ~1000)."""
        if not count or count <= 0:
            return 0.0
        if count >= 1000:
            return 100.0
        return (count / 1000.0) * 100.0

    def _photo_quality_score(self, vision_data: dict[str, Any] | None) -> float:
        """Score based on extracted vision attributes (e.g. well-lit, professional)."""
        if not vision_data:
            return 0.0
        
        labels = vision_data.get("labels", [])
        score = 50.0
        
        quality_keywords = {"lighting", "professional", "food photography", "high resolution", "ambience"}
        for label in labels:
            if any(keyword in label.get("description", "").lower() for keyword in quality_keywords):
                score += (label.get("score", 0.0) * 20)
        
        return min(score, 100.0)

    def _website_score(self, website: str | None) -> float:
        """Score based on website presence."""
        return 100.0 if website else 0.0

    def _audience_match_score(self, target_audience: str | None) -> float:
        """Score based on how well the audience matches target profile."""
        if not target_audience:
            return 50.0
        
        # Simple heuristic: longer, more specific description indicates a clearer audience
        length = len(target_audience)
        return min(50.0 + (length / 5), 100.0)

    def _marketing_potential_score(self, ai_analysis: dict[str, Any] | None) -> float:
        """Score based on AI's summary/features."""
        if not ai_analysis:
            return 50.0
        # If AI successfully extracted fields, assume higher potential
        score = 50.0
        if ai_analysis.get("restaurant_type"):
            score += 15
        if ai_analysis.get("ambience"):
            score += 15
        if ai_analysis.get("ai_summary"):
            score += 20
        return min(score, 100.0)

    def _online_presence_score(self, restaurant_data: dict[str, Any]) -> float:
        """Combine website, google maps URL, photos presence."""
        score = 0.0
        if restaurant_data.get("website"):
            score += 40
        if restaurant_data.get("google_maps_url"):
            score += 30
        if restaurant_data.get("photo_reference"):
            score += 30
        return score
