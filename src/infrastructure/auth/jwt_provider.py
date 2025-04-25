import os
import jwt
from datetime import datetime, timedelta, timezone # Import timezone
from core.entities.user import User # Assuming User model is defined correctly

class JWTProvider:
    def __init__(self):
        # It's safer to raise an error if the secret is missing
        self.secret = os.getenv("JWT_SECRET")
        if not self.secret:
            raise ValueError("JWT_SECRET environment variable not set.")
        self.algorithm = "HS256"
        self.expiry_hours = 24

    def generate_token(self, user: User) -> str:
        """Generates a JWT token for the given user."""
        if not isinstance(user, User):
             raise TypeError("Input must be a User object")


        payload = {
            "email": user.email,
            # Use timezone aware datetime
            "exp": datetime.now(timezone.utc) + timedelta(hours=self.expiry_hours),
            "iat": datetime.now(timezone.utc) # Optional: Issued at time
        }
        try:
            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            return token
        except Exception as e:
            # Log the error for debugging
            raise # Re-raise the exception to indicate failure

    def decode_token(self, token: str) -> dict | None:
        """Decodes a JWT token and returns the payload or None if invalid."""
        try:
            # Decode the token
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            # 'sub' will be a string here, which is usually fine
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError as e:
            return None
        except Exception as e:
            # Catch any other unexpected errors during decoding
            return None
