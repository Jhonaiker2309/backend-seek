import os
from mangum import Mangum
from main import app  # Import your FastAPI instance from main.py

# Retrieves the base path from the environment variable defined in template.yml
# Ensure that the StageName in template.yml matches (e.g., /dev)
# If you are not using stages or deploying at the root, you can omit api_gateway_base_path
stage = os.environ.get('API_GATEWAY_BASE_PATH', '/')

# Wrap your FastAPI app with Mangum
handler = Mangum(app, api_gateway_base_path=stage)