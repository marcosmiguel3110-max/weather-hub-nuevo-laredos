from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.logger import logger

security = HTTPBearer(auto_error=False)

async def verify_master_token(request: Request) -> bool:
    try:
        token = request.headers.get("X-Newser-Token")
        
        if not token:
            logger.warning(f"Access denied: Missing X-Newser-Token from {request.client.host}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: X-Newser-Token required"
            )
        
        if token != settings.MASTER_TOKEN:
            logger.warning(f"Access denied: Invalid token from {request.client.host}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid X-Newser-Token"
            )
        
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def optional_token_check(request: Request) -> bool:
    try:
        token = request.headers.get("X-Newser-Token")
        if not token:
            return False
        
        if token != settings.MASTER_TOKEN:
            return False
        
        return True
    except Exception as e:
        logger.error(f"Optional token check error: {e}")
        return False
