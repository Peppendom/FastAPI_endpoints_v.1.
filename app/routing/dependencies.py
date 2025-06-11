# Third-pary libraries
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

# Modules
from app.business_logic import services
from app.config import PAYLOAD_MAX_SIZE


security = HTTPBearer()


def validate_token(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the provided JWT token.

    - extracts Bearer token from Authorization header;
    - raises 403 if the token is missing;
    - raises 401 if the token is invalid or expired;
    - returns the token payload on success.
    """
    if not services.JWT.validate_token(token.credentials):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token"
        )
    return token.credentials


async def validate_payload_size(request: Request):
    """
    Asynchronously validates payload size.

    - retrieves reqiest body;
    - compares it to the configured maximum payload size;
    - raises 413 if payload exceeds the limit;
    - returns nothing.
    """
    body = await request.body()
    if len(body) > PAYLOAD_MAX_SIZE:
        raise HTTPException(
            status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail = "Request is too large"
        )
