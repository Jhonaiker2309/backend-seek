import os
from mangum import Mangum
from main import app

stage = os.getenv("API_GATEWAY_BASE_PATH")

handler = Mangum(app)