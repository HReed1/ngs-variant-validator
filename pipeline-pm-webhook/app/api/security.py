import hmac
import hashlib
from fastapi import Request, HTTPException, Header
from app.config import settings

async def verify_github_signature(
    request: Request, 
    x_hub_signature_256: str = Header(None)
) -> bytes:
    """
    Validates the GitHub HMAC signature.
    Returns the raw payload bytes if successful, raises 401 if invalid.
    """
    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="Missing signature header")
        
    payload_body = await request.body()
    
    hash_object = hmac.new(
        settings.GITHUB_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    if not hmac.compare_digest(expected_signature, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
    return payload_body