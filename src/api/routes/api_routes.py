from api.handlers import task_handlers, auth_handlers

routes = [
    {
        "path": "/auth/register",
        "method": "POST",
        "handler": auth_handlers.register_user,
        "protected": False
    },
    {
        "path": "/auth/login",
        "method": "POST",
        "handler": auth_handlers.login_user,
        "protected": False
    },
    {
        "path": "/tasks",
        "method": "GET",
        "handler": task_handlers.get_tasks,
        "protected": True
    },
    {
        "path": "/tasks",
        "method": "POST",
        "handler": task_handlers.create_task,
        "protected": True
    },
    {
        "path": "/tasks/{taskId}",
        "method": "PUT",
        "handler": task_handlers.update_task,
        "protected": True
    },
    {
        "path": "/tasks/{taskId}",
        "method": "DELETE",
        "handler": task_handlers.delete_task,
        "protected": True
    }
]