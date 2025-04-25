import json
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.handlers import auth_handlers, task_handlers

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"], # Allow all HTTP methods
    allow_headers=["*"], # Allow all headers
)

# Authentication routes
@app.post("/auth/register")
async def register_user(request: Request):
    """
    Handles user registration.
    """
    event = {"body": await request.body()}
    context = {}
    # --- Modification to handle the handler's response ---
    result = auth_handlers.register_user(event, context)
    status_code = result.get('statusCode', 500)
    headers = result.get('headers', {})
    try:
        # Parse the body as JSON
        body_data = json.loads(result.get('body', '{}'))
    except (json.JSONDecodeError, TypeError):
        # If the body is not valid JSON or None, handle the error
        body_data = {"error": "Invalid body format from handler"}
        if status_code < 400: status_code = 500 # Mark as error if body parsing fails

    return JSONResponse(content=body_data, status_code=status_code, headers=headers)


@app.post("/auth/login")
async def login_user(request: Request):
    """
    Handles user login.
    """
    event = {"body": await request.body()}
    context = {}
    # --- Modification to handle the handler's response ---
    result = auth_handlers.login_user(event, context)
    status_code = result.get('statusCode', 500) # Get the status code from the result
    headers = result.get('headers', {}) # Get the headers from the result

    try:
        # Parse the body as JSON
        body_data = json.loads(result.get('body', '{}'))
    except (json.JSONDecodeError, TypeError):
        # If the body is not valid JSON or None, handle the error
        body_data = {"error": "Invalid body format from handler"}
        if status_code < 400: status_code = 500 # Mark as error if body parsing fails

    # Return a JSONResponse with the parsed content, correct status code, and headers
    return JSONResponse(content=body_data, status_code=status_code, headers=headers)
    # --- End Modification --


@app.get("/tasks")
async def get_tasks(request: Request):
    """
    Retrieves all tasks for the authenticated user.
    """
    event = {"headers": dict(request.headers)}
    context = {}
    result = task_handlers.get_tasks(event, context)
    status_code = result.get('statusCode', 500)
    headers = result.get('headers', {})
    try:
        body_data = json.loads(result.get('body', '[]'))
    except (json.JSONDecodeError, TypeError):
        body_data = {"error": "Invalid body format from handler"}
        if status_code < 400: status_code = 500
    return JSONResponse(content=body_data, status_code=status_code, headers=headers)

@app.post("/tasks")
async def create_task(request: Request):
    """
    Creates a new task
    """
    event = {"body": await request.body(), "headers": dict(request.headers)}
    context = {}
    result = task_handlers.create_task(event, context)
    status_code = result.get('statusCode', 500)
    headers = result.get('headers', {})
    try:
        body_data = json.loads(result.get('body', '{}'))
    except (json.JSONDecodeError, TypeError):
        body_data = {"error": "Invalid body format from handler"}
        if status_code < 400: status_code = 500
    return JSONResponse(content=body_data, status_code=status_code, headers=headers)


@app.put("/tasks/{task_id}")
async def update_task(task_id: str, request: Request):
    """
    Updates an existing task.
    """
    event = {
        "body": await request.body(),
        "pathParameters": {"taskId": task_id},
        "headers": dict(request.headers)
    }
    context = {}
    result = task_handlers.update_task(event, context)
    status_code = result.get('statusCode', 500)
    headers = result.get('headers', {})
    try:
        body_data = json.loads(result.get('body', '{}'))
    except (json.JSONDecodeError, TypeError):
        body_data = {"error": "Invalid body format from handler"}
        if status_code < 400: status_code = 500
    return JSONResponse(content=body_data, status_code=status_code, headers=headers)


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str, request: Request):
    """
    Deletes a task.
    """
    event = {
        "pathParameters": {"taskId": task_id},
        "headers": dict(request.headers)
    }
    context = {}
    result = task_handlers.delete_task(event, context)
    status_code = result.get('statusCode', 500)
    headers = result.get('headers', {})
    if status_code == 204:
        return Response(status_code=status_code, headers=headers)
    else:
        try:
            body_data = json.loads(result.get('body', '{}'))
        except (json.JSONDecodeError, TypeError):
            body_data = {"error": "Invalid body format from handler"}
            if status_code < 400: status_code = 500
        return JSONResponse(content=body_data, status_code=status_code, headers=headers)
