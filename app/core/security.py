from fastapi import Header, HTTPException, status
from app.core.config import get_settings

settings = get_settings()

def verify_api_key(x_api_key: str | None = Header(default=None)) -> str | None:
    """Verify the API key passed in the header if configured."""
    if not settings.API_KEY:
        # No auth required if API_KEY is empty
        return None

    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key"
        )
    return x_api_key
