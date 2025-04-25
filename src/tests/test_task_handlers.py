# src/tests/test_task_handlers.py
import pytest
from unittest.mock import patch
from api.handlers.task_handlers import create_task_handler

@patch("core.services.task_service.TaskService")
def test_create_task_success(mock_service):
    mock_service.return_value.create_task.return_value = {"id": "123"}
    event = {
        "body": json.dumps({"title": "Test"}),
        "headers": {"Authorization": "Bearer valid_token"}
    }
    response = create_task_handler(event, None)
    assert response["statusCode"] == 201