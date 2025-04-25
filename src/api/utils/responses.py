import json
from typing import Union, Dict, Any

def success(status_code: int, data: Any) -> Dict[str, Any]:
    """
    Formats a successful response for API Gateway Lambda Proxy.

    Args:
        status_code: HTTP status code (e.g., 200, 201).
        data: The data to include in the response body.
              Can be a dictionary, list, or any object serializable by json.dumps.

    Returns:
        A dictionary formatted for Lambda Proxy response.
    """
    # Attempt to serialize the data directly
    try:
        body_content = json.dumps(data)
    except TypeError as e:
        # If direct serialization fails (e.g., non-serializable objects like ObjectId without encoder)
        # You could add specific handling here or return a generic internal error.
        # For now, we return a generic internal server error.
        return error(500, "Internal server error: Failed to serialize response data")

    return {
        "statusCode": status_code,
        "body": body_content,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    }

def error(status_code: int, detail: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Formats an error response for API Gateway Lambda Proxy.

    Args:
        status_code: HTTP status code (e.g., 400, 404, 500).
        detail: The error detail. Can be a string with a simple message
                or a dictionary with more details (e.g., {"field": "email", "message": "Invalid format"}).

    Returns:
        A dictionary formatted for Lambda Proxy response.
    """
    if isinstance(detail, str):
        body_data = {"error": detail}
    elif isinstance(detail, dict):
        body_data = detail
    else:
        body_data = {"error": str(detail)}

    return {
        "statusCode": status_code,
        "body": json.dumps(body_data),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    }