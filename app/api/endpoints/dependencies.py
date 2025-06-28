from fastapi import HTTPException, status, Header

from app.core.config import settings


async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Некорректный API Key"
        )
