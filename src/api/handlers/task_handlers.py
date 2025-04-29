import logging
from typing import Dict, Any, List
from pydantic import ValidationError
import json

from core.services.task_service import TaskService
from core.entities.task import Task, TaskUpdate
from core.exceptions.task_errors import TaskNotFoundError, TaskPermissionError
from core.exceptions.auth_errors import AuthenticationError

from infrastructure.database.mongo_repositories import MongoTaskRepository
from infrastructure.auth.jwt_provider import JWTProvider
from api.utils.responses import success, error

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    task_repository = MongoTaskRepository()
    task_service = TaskService(repository=task_repository)
    jwt_provider = JWTProvider()
except Exception as setup_error:
    logger.error(f"Error setting up task handlers dependencies: {setup_error}")
    raise setup_error

def get_tasks(event: Dict[str, Any], context: Any) -> Dict:
    try:
        # 1. Extract Token from headers
        headers = event.get("headers", {})
        auth_header = headers.get("authorization", headers.get("Authorization"))

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Missing or invalid Authorization header")
            return error(401, "Authorization header missing or invalid")

        token = auth_header.split(" ")[1]

        # 2. Decode Token using JWTProvider
        user = jwt_provider.decode_token(token)

        # 3. Check if token decoding was successful
        if user is None:
            logger.warning("Token validation failed (invalid, expired, or other error)")
            return error(401, "Invalid or expired token")

        # 4. Proceed with getting tasks if user is valid
        user_email = user.get("email")
        if not user_email:
             logger.error("Token payload does not contain email")
             return error(401, "Invalid token payload")

        logger.info(f"Authenticated user: {user_email}")

        tasks: List[Task] = task_service.get_user_tasks(user_email=user_email)

        tasks_data = [
            t.model_dump(exclude={"user_email"}) if hasattr(t, 'model_dump') else t.dict(exclude={"user_email"})
            for t in tasks
        ]
        for i, task in enumerate(tasks):
             tasks_data[i]['id'] = str(task.id)

        return success(200, tasks_data)

    except TaskPermissionError as e:
        logger.warning(f"Authentication error in get_tasks: {e}")
        return error(401, str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_tasks: {e}", exc_info=True) # Log full traceback
        return error(500, "Internal server error")

def create_task(event: Dict[str, Any], context: Any) -> Dict:
    try:
        headers = event.get("headers", {})
        auth_header = headers.get("authorization", headers.get("Authorization"))
        if not auth_header or not auth_header.startswith("Bearer "):
            return error(401, "Authorization header missing or invalid")
        token = auth_header.split(" ")[1]
        user = jwt_provider.decode_token(token)
        if user is None:
            return error(401, "Invalid or expired token")
        user_email = user.get("email")
        if not user_email:
             return error(401, "Invalid token payload")
        logger.info(f"Authenticated user for create_task: {user_email}")
        body_str = event.get("body")
        if not body_str:
            return error(400, "Request body is missing")
        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            return error(400, "Invalid JSON format")

        body["user_email"] = user_email
        title = body.get("title")
        description = body.get("description")

        try:
            task_data = Task(**body)
        except ValidationError as e:
            return error(400, f"Validation Error: {e.errors()}")

        new_task = task_service.create_task(title=title, user_email=user_email, description=description)

        # Serialize response
        response_data = new_task.model_dump(exclude={"user_email"}) if hasattr(new_task, 'model_dump') else new_task.dict(exclude={"user_email"})
        response_data['id'] = str(new_task.id)

        return success(201, response_data)

    except AuthenticationError as e:
        return error(401, str(e))
    except ValidationError as e:
         return error(400, f"Creation Validation Error: {e.errors()}")
    except Exception as e:
        logger.error(f"Unexpected error in create_task: {e}", exc_info=True)
        return error(500, "Internal server error")


def update_task(event: Dict[str, Any], context: Any) -> Dict:
    try:
        headers = event.get("headers", {})
        auth_header = headers.get("authorization", headers.get("Authorization"))
        if not auth_header or not auth_header.startswith("Bearer "):
            return error(401, "Authorization header missing or invalid")
        token = auth_header.split(" ")[1]
        user = jwt_provider.decode_token(token)
        if user is None:
            return error(401, "Invalid or expired token")
        user_email = user.get("email")
        if not user_email:
             return error(401, "Invalid token payload")
        logger.info(f"Authenticated user for update_task: {user_email}")

        task_id = event.get("pathParameters", {}).get("taskId")
        if not task_id:
            return error(400, "Task ID missing in path")

        body_str = event.get("body")
        if not body_str:
            return error(400, "Request body is missing")
        try:
            body = json.loads(body_str)
        except json.JSONDecodeError:
            return error(400, "Invalid JSON format")

        body.pop("user_email", None)
        body.pop("id", None)

        try:
            update_data = TaskUpdate(**body).model_dump(exclude_unset=True)
        except ValidationError as e:
            return error(400, f"Validation Error: {e.errors()}")

        updated_task = task_service.update_task(task_id=task_id, updates=update_data, user_email=user_email)

        if updated_task is None:
             return error(404, f"Task with id {task_id} not found or not authorized to update.")

        response_data = updated_task.model_dump(exclude={"user_email"}) if hasattr(updated_task, 'model_dump') else updated_task.dict(exclude={"user_email"})
        response_data['id'] = task_id

        return success(200, response_data)

    except TaskNotFoundError:
        return error(404, f"Task with id {task_id} not found.")
    except AuthenticationError as e:
        return error(403, str(e))
    except ValidationError as e:
         return error(400, f"Update Validation Error: {e.errors()}")
    except Exception as e:
        logger.error(f"Unexpected error in update_task: {e}", exc_info=True)
        return error(500, "Internal server error")


def delete_task(event: Dict[str, Any], context: Any) -> Dict:
    try:
        headers = event.get("headers", {})
        auth_header = headers.get("authorization", headers.get("Authorization"))
        if not auth_header or not auth_header.startswith("Bearer "):
            return error(401, "Authorization header missing or invalid")
        token = auth_header.split(" ")[1]
        user = jwt_provider.decode_token(token)
        if user is None:
            return error(401, "Invalid or expired token")
        user_email = user.get("email")
        if not user_email:
             return error(401, "Invalid token payload")
        logger.info(f"Authenticated user for delete_task: {user_email}")
        # --- End Authentication Check ---

        task_id = event.get("pathParameters", {}).get("taskId")
        if not task_id:
            return error(400, "Task ID missing in path")

        deleted = task_service.delete_task(task_id=task_id, user_email=user_email)

        if not deleted:
            # Task not found or user not authorized
             return error(404, f"Task with id {task_id} not found or not authorized to delete.")

        # No body needed for 204 response
        return success(204, None)

    except TaskNotFoundError:
         return error(404, f"Task with id {task_id} not found.")
    except AuthenticationError as e:
        return error(403, str(e))
    except Exception as e:
        logger.error(f"Unexpected error in delete_task: {e}", exc_info=True)
        return error(500, "Internal server error")
