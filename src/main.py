import json
import logging
from typing import List
from fastapi import FastAPI, Request, Response, HTTPException, status, Path, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from bson import ObjectId

from api.handlers import auth_handlers, task_handlers
from api.schemas.auth_schemas import UserRegisterSchema, UserLoginSchema, AuthResponseSchema, ErrorDetailSchema
from api.schemas.task_schemas import TaskResponseSchema, TaskCreateSchema, TaskUpdateSchema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security_scheme = HTTPBearer()

app = FastAPI(
    title="Task Manager API",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration and authentication endpoints",
        },
        {
            "name": "Tasks",
            "description": "Operations on user tasks",
        },
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string", format="objectid", example="60d5ecf3a3b4b5b6c7d8e9f0")
        return json_schema

def process_handler_response(result: dict, success_status: int = status.HTTP_200_OK) -> Response:
    """Processes the dictionary response from handlers into a FastAPI Response."""
    status_code = result.get('statusCode', status.HTTP_500_INTERNAL_SERVER_ERROR)
    headers = result.get('headers', {})
    body_str = result.get('body')

    if status_code == status.HTTP_204_NO_CONTENT:
        return Response(status_code=status_code, headers=headers)

    try:
        body_data = json.loads(body_str) if body_str else {}
        return JSONResponse(content=body_data, status_code=status_code, headers=headers)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Error parsing handler response: {e}")
        return JSONResponse(
            content={"detail": "Internal error in response format"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=headers
        )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handles any unhandled exceptions."""
    logger.exception(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

@app.post(
    "/auth/register",
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    response_model=AuthResponseSchema,
    responses={
        400: {"model": ErrorDetailSchema},
        500: {"model": ErrorDetailSchema}
    }
)
async def register_user(user_data: UserRegisterSchema):
    """Registers a new user."""
    try:
        event = {"body": user_data.model_dump_json()}
        result = auth_handlers.register_user(event, {})
        return process_handler_response(result, status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post(
    "/auth/login",
    tags=["Authentication"],
    response_model=AuthResponseSchema,
    responses={
        401: {"model": ErrorDetailSchema},
        500: {"model": ErrorDetailSchema}
    }
)
async def login_user(credentials: UserLoginSchema):
    """Logs in a user."""
    try:
        event = {"body": credentials.model_dump_json()}
        result = auth_handlers.login_user(event, {})
        return process_handler_response(result)
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get(
    "/tasks",
    tags=["Tasks"],
    response_model=List[TaskResponseSchema],
    responses={
        401: {"model": ErrorDetailSchema},
        500: {"model": ErrorDetailSchema}
    },
    dependencies=[Depends(security_scheme)]
)
async def get_tasks(request: Request):
    """Gets all tasks for the authenticated user."""
    try:
        event = {"headers": dict(request.headers)}
        result = task_handlers.get_tasks(event, {})
        return process_handler_response(result)
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tasks")

@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
    response_model=TaskResponseSchema,
    responses={
        400: {"model": ErrorDetailSchema},
        401: {"model": ErrorDetailSchema},
        500: {"model": ErrorDetailSchema}
    },
    dependencies=[Depends(security_scheme)]
)
async def create_task(request: Request, task_data: TaskCreateSchema):
    """Creates a new task for the authenticated user."""
    try:
        event = {
            "body": task_data.model_dump_json(),
            "headers": dict(request.headers)
        }
        result = task_handlers.create_task(event, {})
        return process_handler_response(result, status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to create task")

@app.put(
    "/tasks/{task_id}",
    tags=["Tasks"],
    response_model=TaskResponseSchema,
    responses={
        400: {"model": ErrorDetailSchema},
        401: {"model": ErrorDetailSchema},
        404: {"model": ErrorDetailSchema},
        500: {"model": ErrorDetailSchema}
    },
    dependencies=[Depends(security_scheme)]
)
async def update_task(
    task_id: str = Path(..., example="60d5ecf3a3b4b5b6c7d8e9f0"),
    task_data: TaskUpdateSchema = Body(...),
    request: Request = None
):
    try:
        event = {
            "body": task_data.model_dump_json(exclude_unset=True),
            "pathParameters": {"taskId": task_id},
            "headers": dict(request.headers) if request else {}
        }
        result = task_handlers.update_task(event, {})
        return process_handler_response(result)
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail="Failed to update task")

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
    responses={
        204: {"description": "Task deleted"},
        401: {"model": ErrorDetailSchema},
        404: {"model": ErrorDetailSchema},
        500: {"model": ErrorDetailSchema}
    },
    dependencies=[Depends(security_scheme)] # Requires authentication
)
async def delete_task(
    task_id: str = Path(..., example="60d5ecf3a3b4b5b6c7d8e9f0"),
    request: Request = None
):
    """Deletes a task for the authenticated user."""
    try:
        event = {
            "pathParameters": {"taskId": task_id},
            "headers": dict(request.headers) if request else {}
        }
        result = task_handlers.delete_task(event, {})
        # Return the response, ensuring 204 code is handled correctly
        return process_handler_response(result, status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete task")