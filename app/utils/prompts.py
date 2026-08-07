"""LLM prompt templates for the application."""

RESTAURANT_ANALYSIS_PROMPT = """
You are an expert hospitality consultant. Analyze the following restaurant data and provide insights.
Data: {restaurant_data}

Provide your analysis in valid JSON format with the following structure:
{{
    "ai_summary": "A concise summary of the restaurant",
    "restaurant_type": "The type of restaurant (e.g. FINE_DINING, CASUAL_DINING)",
    "ambience": "Description of the ambience",
    "target_audience": "Who the primary customers are",
    "premium_score": 8.5
}}
"""

OUTREACH_MESSAGE_PROMPT = """
You are a sales professional. Draft a highly personalized outreach message to the owner of this restaurant.
Restaurant Info: {restaurant_info}
Reason for collaboration: {collaboration_reason}

Write a professional and compelling email template.
"""

COLLABORATION_SCORING_PROMPT = """
Evaluate this restaurant for a potential collaboration.
Restaurant Data: {restaurant_data}

Output JSON format:
{{
    "collaboration_score": 9.2,
    "collaboration_reason": "Why they are a great fit."
}}
"""

RESTAURANT_INTELLIGENCE_PROMPT = """
You are a top-tier restaurant industry analyst. Analyze the following restaurant data and provide deep intelligence.
Restaurant Data: {restaurant_data}

Return valid JSON exactly in this structure:
{{
    "restaurant_type": "Category (e.g. Cafe, Fine Dining)",
    "cuisine_type": "Primary cuisines",
    "estimated_spending": "Budget, Mid Range, Premium, or Luxury",
    "customer_segment": ["Segment 1", "Segment 2"],
    "restaurant_style": "Theme/Style description",
    "strengths": ["Strength 1", "Strength 2"],
    "weaknesses": ["Weakness 1", "Weakness 2"],
    "marketing_maturity": "Low, Medium, or High",
    "branding_quality": "Poor, Fair, Good, or Excellent",
    "online_presence_score": 0.0 to 10.0,
    "ai_summary": "Comprehensive 2-sentence summary",
    "premium_score": 0.0 to 10.0
}}
"""

COLLABORATION_INTELLIGENCE_PROMPT = """
You are a hospitality marketing expert. Evaluate collaboration opportunities for this restaurant.
Evaluate the following types: Instagram Reels, Food Bloggers, Influencer Marketing, Launch Campaign, Paid Ads, Photography, Menu Shoot, Google Reviews Campaign, Event Promotion, Local Influencers, Community Marketing.

Restaurant Data: {restaurant_data}

Return valid JSON exactly in this structure:
{{
    "opportunities": [
        {{
            "type": "Instagram Reels",
            "probability": 0.85,
            "reason": "Explain why this works well for them"
        }}
    ],
    "overall_score": 8.5,
    "top_recommendation": "The absolute best collaboration type"
}}
"""

OPENING_DETECTION_PROMPT = """
Analyze the following restaurant data and signals to determine if it is a new or opening soon restaurant.
Restaurant Data: {restaurant_data}

Return valid JSON exactly in this structure:
{{
    "opening_status": "OPENING_SOON, NEWLY_OPENED, ESTABLISHED, or UNKNOWN",
    "confidence": 0.0 to 1.0,
    "signals": ["Signal 1", "Signal 2"]
}}
"""

OUTREACH_BUNDLE_PROMPT = """
You are an expert sales copywriter. Generate a complete outreach bundle for the following restaurant.
Restaurant Data: {restaurant_data}
Opportunity Data: {opportunity_data}

Return valid JSON exactly in this structure:
{{
    "cold_email": "Professional cold email template",
    "instagram_dm": "Short, engaging IG DM",
    "whatsapp_message": "Friendly WhatsApp message",
    "phone_script": "Short script for a cold call",
    "linkedin_message": "Professional LinkedIn connection message",
    "opening_congrats_message": "Congratulatory message if they are opening soon/newly opened (or empty)",
    "marketing_proposal": "A short, high-level marketing proposal pitch"
}}
"""

AI_DECISION_PROMPT = """
You are a sales director deciding whether to contact a lead today.
Evaluate the following restaurant lead.
Restaurant Data: {restaurant_data}

Return valid JSON exactly in this structure:
{{
    "decision": "YES, NO, or MAYBE",
    "confidence": 0.0 to 1.0,
    "reasoning": "Explain why we should or shouldn't contact them now",
    "expected_roi": "Low, Medium, or High"
}}
"""

OWNER_DISCOVERY_PROMPT = """
You are a web intelligence expert. Extract or infer potential contact information and owner details from the provided data.
Data: {restaurant_data}

Return valid JSON exactly in this structure:
{{
    "owner_name": "Name or null",
    "manager_name": "Name or null",
    "business_email": "Email or null",
    "instagram": "Handle or null",
    "facebook": "Handle or null",
    "linkedin": "Profile or null",
    "confidence": 0.0 to 1.0
}}
"""

COMPETITOR_ANALYSIS_PROMPT = """
You are a market analyst. Evaluate the competition landscape for the following restaurant based on its details and location.
Restaurant Data: {restaurant_data}
Nearby Places: {nearby_places}

Return valid JSON exactly in this structure:
{{
    "competitor_count": 5,
    "competitors": [
        {{
            "name": "Competitor Name",
            "rating": 4.5,
            "review_count": 120,
            "price_level": 2,
            "distance_meters": 500
        }}
    ],
    "competition_score": "High, Medium, or Low",
    "opportunity": "High, Medium, or Low",
    "analysis": "Brief analysis of the competitive landscape"
}}
"""

DAILY_SUMMARY_PROMPT = """
You are a strategic sales manager. Summarize the daily leads into actionable insights for the team.
Daily Data: {daily_data}

Return valid JSON exactly in this structure:
{{
    "date": "YYYY-MM-DD",
    "summary": "Overall summary of today's leads and main opportunities",
    "best_leads_ids": [1, 2],
    "top_premium_ids": [3],
    "most_likely_to_collaborate_ids": [4, 5],
    "opening_soon_ids": [6],
    "high_roi_ids": [7],
    "low_competition_ids": [8]
}}
"""
