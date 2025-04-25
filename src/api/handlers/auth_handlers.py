import json
import logging
from typing import Dict, Any

# Core components
from core.services.auth_service import AuthService
from core.exceptions.auth_errors import UserAlreadyExistsError, InvalidCredentialsError

# Infrastructure components
from infrastructure.database.mongo_repositories import MongoUserRepository
from infrastructure.auth.jwt_provider import JWTProvider

from api.utils.responses import success, error

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    user_repository = MongoUserRepository()
    auth_service = AuthService(repository=user_repository)
    jwt_provider = JWTProvider()
except Exception as setup_error:
    raise setup_error

def register_user(event: Dict[str, Any], context: Any) -> Dict:
    try:
        body_str = event.get("body")
        if not body_str:
            return error(400, "Request body is missing")
        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            return error(400, "Invalid JSON format")
        
        email = body.get("email")
        password = body.get("password")
        
        if not email or not password:
            return error(400, "Email and password are required")
        
        user = auth_service.register_user(email, password)
        token = jwt_provider.generate_token(user)


        response_data = {"email": user.email, "token": token} 

        return success(201, response_data)

    except UserAlreadyExistsError as e:
        return error(409, str(e))
    except ValueError as e:
        return error(400, str(e))
    except Exception as e:
        return error(500, "Internal server error")

def login_user(event: Dict[str, Any], context: Any) -> Dict:
    """Iniciar sesión"""
    try:
        body_str = event.get("body")
        if not body_str:
            return error(400, "Request body is missing")
        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            return error(400, "Invalid JSON format")

        email = body.get("email")
        password = body.get("password")

        if not email or not password:
            return error(400, "Email and password are required")

        # Use the pre-initialized auth_service
        user = auth_service.authenticate_user(email, password)

        # Generate token
        token = jwt_provider.generate_token(user)

        # Return success response including the token and relevant user info
        response_data = {"email": user.email,"token": token}

        return success(200, response_data)

    except InvalidCredentialsError as e:
        # Use 401 Unauthorized for invalid credentials
        return error(401, str(e))
    except ValueError as e: # Catch other validation errors
        return error(400, str(e))
    except Exception as e:
        # Log the full exception for unexpected errors
        return error(500, "Internal server error")