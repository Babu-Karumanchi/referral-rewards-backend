from typing import Annotated
from fastapi import Depends, HTTPException, status, Header
from typing import Optional

async def require_admin(authorization: Optional[str] = Header(None)) -> bool:
    """
    Admin-only protection (Bearer token simulation)
    Real JWT would check token claims
    """
    if not authorization or not authorization.startswith("Bearer admin-token"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Admin access required. Use: Authorization: Bearer admin-token"
        )
    return True
