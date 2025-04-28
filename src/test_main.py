import json
import unittest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import status
from fastapi.testclient import TestClient

# Define the environment variables needed before imports happen
mock_environ = {
    "JWT_SECRET": "test-secret-for-unit-tests",
    "MONGO_URI": "mongodb://mock:mock@localhost/mockdb",
    "DATABASE_NAME": "mockdb"
}
# Create a patcher that will be started/stopped manually
environ_patcher = patch.dict(os.environ, mock_environ)

def setUpModule():
    """Set up environment variables before any tests run."""
    print("Setting up module with mock environment variables...")
    environ_patcher.start()
    global app, client
    from main import app as imported_app
    app = imported_app
    client = TestClient(app)
    print("Module setup complete.")

def tearDownModule():
    """Clean up environment variables after all tests have run."""
    print("Tearing down module...")
    environ_patcher.stop()
    print("Module teardown complete.")

# --- Mock Handler Responses ---
# Define standard responses that handlers might return
MOCK_SUCCESS_RESPONSE = {"statusCode": 200, "body": json.dumps({"message": "Success"}), "headers": {"X-Custom-Header": "value"}}
MOCK_CREATED_RESPONSE = {"statusCode": 201, "body": json.dumps({"id": "123", "message": "Created"})}
MOCK_NO_CONTENT_RESPONSE = {"statusCode": 204, "body": None, "headers": {}} # Body is often None or empty for 204
MOCK_BAD_REQUEST_RESPONSE = {"statusCode": 400, "body": json.dumps({"detail": "Invalid input"})}
MOCK_UNAUTHORIZED_RESPONSE = {"statusCode": 401, "body": json.dumps({"detail": "Unauthorized"})}
MOCK_FORBIDDEN_RESPONSE = {"statusCode": 403, "body": json.dumps({"detail": "Forbidden"})}
MOCK_NOT_FOUND_RESPONSE = {"statusCode": 404, "body": json.dumps({"detail": "Not Found"})}
MOCK_CONFLICT_RESPONSE = {"statusCode": 409, "body": json.dumps({"detail": "Conflict"})}
MOCK_SERVER_ERROR_RESPONSE = {"statusCode": 500, "body": json.dumps({"detail": "Internal handler error"})}
MOCK_MALFORMED_HANDLER_RESPONSE = {"statusCode": 200, "body": "{invalid json"} # Success code but invalid body


# Remove the @patch.dict decorator from the class
class TestMainApp(unittest.TestCase):

    # --- Test CORS Middleware ---
    def test_cors_headers(self):
        """Test if CORS headers are present in the response for an OPTIONS request."""
        response = client.options("/auth/login")
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED])
        if response.status_code == status.HTTP_200_OK:
             self.assertEqual(response.headers.get("access-control-allow-origin"), "*")
             self.assertEqual(response.headers.get("access-control-allow-credentials"), "true")
             self.assertIn("POST", response.headers.get("access-control-allow-methods", ""))

    # --- Test Global Exception Handler ---
    # This test now verifies the route's specific exception handling
    @patch('api.handlers.auth_handlers.login_user', side_effect=Exception("Unexpected crash"))
    def test_route_exception_handling_login(self, mock_login):
        """Test the route's specific exception handling catches handler errors."""
        response = client.post("/auth/login", json={"email": "a", "password": "b"})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {"detail": "Failed to process login request."})
        mock_login.assert_called_once() # Ensure the handler was called

    # --- Test Authentication Routes ---

    @patch('api.handlers.auth_handlers.register_user')
    def test_register_user_success(self, mock_register):
        """Test successful user registration."""
        mock_register.return_value = MOCK_CREATED_RESPONSE
        user_data = {"email": "test@example.com", "password": "password123"}

        response = client.post("/auth/register", json=user_data)

        # Assert handler call
        call_args, _ = mock_register.call_args
        event_arg = call_args[0]
        self.assertEqual(json.loads(event_arg.get("body")), user_data)

        # Assert response processing
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), json.loads(MOCK_CREATED_RESPONSE["body"]))

    @patch('api.handlers.auth_handlers.register_user')
    def test_register_user_conflict(self, mock_register):
        """Test user registration conflict (user already exists)."""
        mock_register.return_value = MOCK_CONFLICT_RESPONSE
        user_data = {"email": "existing@example.com", "password": "password123"}

        response = client.post("/auth/register", json=user_data)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json(), json.loads(MOCK_CONFLICT_RESPONSE["body"]))
        mock_register.assert_called_once()

    @patch('api.handlers.auth_handlers.login_user')
    def test_login_user_success(self, mock_login):
        """Test successful user login."""
        mock_login.return_value = MOCK_SUCCESS_RESPONSE
        login_data = {"email": "test@example.com", "password": "password123"}

        response = client.post("/auth/login", json=login_data)

        # Assert handler call
        call_args, _ = mock_login.call_args
        event_arg = call_args[0]
        self.assertEqual(json.loads(event_arg.get("body")), login_data)

        # Assert response processing
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), json.loads(MOCK_SUCCESS_RESPONSE["body"]))
        self.assertEqual(response.headers.get("x-custom-header"), "value")

    @patch('api.handlers.auth_handlers.login_user')
    def test_login_user_invalid_credentials(self, mock_login):
        """Test user login with invalid credentials."""
        mock_login.return_value = MOCK_UNAUTHORIZED_RESPONSE
        login_data = {"email": "test@example.com", "password": "wrongpassword"}

        response = client.post("/auth/login", json=login_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), json.loads(MOCK_UNAUTHORIZED_RESPONSE["body"]))
        mock_login.assert_called_once()

    @patch('api.handlers.auth_handlers.login_user')
    def test_login_user_handler_server_error(self, mock_login):
        """Test login when the handler itself returns a 500."""
        mock_login.return_value = MOCK_SERVER_ERROR_RESPONSE
        login_data = {"email": "test@example.com", "password": "password123"}

        response = client.post("/auth/login", json=login_data)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), json.loads(MOCK_SERVER_ERROR_RESPONSE["body"]))
        mock_login.assert_called_once()

    @patch('api.handlers.auth_handlers.login_user')
    def test_login_user_malformed_handler_response(self, mock_login):
        """Test login when the handler returns a malformed body."""
        mock_login.return_value = MOCK_MALFORMED_HANDLER_RESPONSE

        response = client.post("/auth/login", json={"email": "a", "password": "b"})

        # process_handler_response should catch the JSONDecodeError and return 500
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        response_json = response.json()
        self.assertEqual(response_json["detail"], "Invalid response format received from internal handler.")
        self.assertEqual(response_json["handler_status_code"], 200) # Original status code from handler
        self.assertEqual(response_json["handler_response_preview"], MOCK_MALFORMED_HANDLER_RESPONSE["body"])
        mock_login.assert_called_once()


    # --- Test Task Routes ---

    @patch('api.handlers.task_handlers.get_tasks')
    def test_get_tasks_success(self, mock_get_tasks):
        """Test successfully getting tasks."""
        mock_get_tasks.return_value = MOCK_SUCCESS_RESPONSE
        headers = {"Authorization": "Bearer valid_token"}

        response = client.get("/tasks", headers=headers)

        # Assert handler call
        call_args, _ = mock_get_tasks.call_args
        event_arg = call_args[0]
        self.assertEqual(event_arg.get("headers", {}).get("authorization"), headers["Authorization"])

        # Assert response processing
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), json.loads(MOCK_SUCCESS_RESPONSE["body"]))
        mock_get_tasks.assert_called_once()

    @patch('api.handlers.task_handlers.get_tasks')
    def test_get_tasks_unauthorized(self, mock_get_tasks):
        """Test getting tasks when handler determines unauthorized."""
        mock_get_tasks.return_value = MOCK_UNAUTHORIZED_RESPONSE # e.g., token invalid
        headers = {"Authorization": "Bearer invalid_token"}

        response = client.get("/tasks", headers=headers)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), json.loads(MOCK_UNAUTHORIZED_RESPONSE["body"]))
        mock_get_tasks.assert_called_once()

    @patch('api.handlers.task_handlers.create_task')
    def test_create_task_success(self, mock_create_task):
        """Test successfully creating a task."""
        mock_create_task.return_value = MOCK_CREATED_RESPONSE
        headers = {"Authorization": "Bearer valid_token"}
        task_data = {"title": "New Task", "description": "Do something"}

        response = client.post("/tasks", headers=headers, json=task_data)

        # Assert handler call
        call_args, _ = mock_create_task.call_args
        event_arg = call_args[0]
        self.assertEqual(event_arg.get("headers", {}).get("authorization"), headers["Authorization"])
        self.assertEqual(json.loads(event_arg.get("body")), task_data)

        # Assert response processing
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), json.loads(MOCK_CREATED_RESPONSE["body"]))
        mock_create_task.assert_called_once()

    @patch('api.handlers.task_handlers.update_task')
    def test_update_task_success(self, mock_update_task):
        """Test successfully updating a task."""
        mock_update_task.return_value = MOCK_SUCCESS_RESPONSE
        headers = {"Authorization": "Bearer valid_token"}
        task_id = "task123"
        update_data = {"title": "Updated Title", "completed": True}

        response = client.put(f"/tasks/{task_id}", headers=headers, json=update_data)

        # Assert handler call
        call_args, _ = mock_update_task.call_args
        event_arg = call_args[0]
        self.assertEqual(event_arg.get("headers", {}).get("authorization"), headers["Authorization"])
        self.assertEqual(event_arg.get("pathParameters", {}).get("taskId"), task_id)
        self.assertEqual(json.loads(event_arg.get("body")), update_data)

        # Assert response processing
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), json.loads(MOCK_SUCCESS_RESPONSE["body"]))
        mock_update_task.assert_called_once()

    @patch('api.handlers.task_handlers.update_task')
    def test_update_task_not_found(self, mock_update_task):
        """Test updating a task that is not found."""
        mock_update_task.return_value = MOCK_NOT_FOUND_RESPONSE
        headers = {"Authorization": "Bearer valid_token"}
        task_id = "nonexistent_task"
        update_data = {"title": "Updated Title"}

        response = client.put(f"/tasks/{task_id}", headers=headers, json=update_data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), json.loads(MOCK_NOT_FOUND_RESPONSE["body"]))
        mock_update_task.assert_called_once()

    @patch('api.handlers.task_handlers.delete_task')
    def test_delete_task_success(self, mock_delete_task):
        """Test successfully deleting a task."""
        mock_delete_task.return_value = MOCK_NO_CONTENT_RESPONSE
        headers = {"Authorization": "Bearer valid_token"}
        task_id = "task123"

        response = client.delete(f"/tasks/{task_id}", headers=headers)

        call_args, _ = mock_delete_task.call_args
        event_arg = call_args[0]
        self.assertEqual(event_arg.get("headers", {}).get("authorization"), headers["Authorization"])
        self.assertEqual(event_arg.get("pathParameters", {}).get("taskId"), task_id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        mock_delete_task.assert_called_once()

    @patch('api.handlers.task_handlers.delete_task')
    def test_delete_task_not_found(self, mock_delete_task):
        """Test deleting a task that is not found."""
        mock_delete_task.return_value = MOCK_NOT_FOUND_RESPONSE
        headers = {"Authorization": "Bearer valid_token"}
        task_id = "nonexistent_task"

        response = client.delete(f"/tasks/{task_id}", headers=headers)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), json.loads(MOCK_NOT_FOUND_RESPONSE["body"]))
        mock_delete_task.assert_called_once()


if __name__ == '__main__':
    # The imports will happen safely inside setUpModule now
    unittest.main(argv=['first-arg-is-ignored'], exit=False)