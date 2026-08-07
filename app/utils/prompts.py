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
