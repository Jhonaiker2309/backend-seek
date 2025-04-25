import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from typing import Optional, Dict
from infrastructure.auth.jwt_provider import JWTProvider

class JWTBearer(HTTPBearer):
    """
    Middleware to validate JWT tokens.
    """
    def __init__(self):
        """
        Initializes the JWTBearer middleware with a JWTProvider instance.
        """
        super().__init__(auto_error=True)
        self.provider = JWTProvider()

    async def __call__(self, request: Request) -> Optional[Dict]:
        """
        Validates the JWT token from the request.

        Args:
            request: The incoming HTTP request.

        Returns:
            The decoded token as a dictionary if valid.

        Raises:
            HTTPException: If the token is invalid or expired.
        """
        credentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=403, detail="Invalid token")
        
        try:
            # Decode the token using the JWTProvider
            decoded = self.provider.decode_token(credentials.credentials)
            return decoded
        except jwt.ExpiredSignatureError:
            # Raise an exception if the token has expired
            raise HTTPException(status_code=403, detail="Token expired")
        except jwt.InvalidTokenError:
            # Raise an exception if the token is invalid
            raise HTTPException(status_code=403, detail="Invalid token")

def get_current_user(event: Dict) -> Dict:
    """
    Extracts the current user from the JWT token in Lambda events.

    Args:
        event: The Lambda event containing the request headers.

    Returns:
        The decoded token as a dictionary.

    Raises:
        HTTPException: If the token is missing or invalid.
    """
    try:
        # Extract the token from the Authorization header
        token = event["headers"].get("authorization", "").split("Bearer ")[1]
        decoded = JWTProvider().decode_token(token)
        return decoded
    except Exception:
        # Raise an exception if the token is missing or invalid
        raise HTTPException(status_code=401, detail="Unauthorized")