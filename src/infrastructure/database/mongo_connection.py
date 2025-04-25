import os
from pymongo import MongoClient
from pymongo.database import Database
# Import OperationFailure as well
from pymongo.errors import ConnectionFailure, ConfigurationError, OperationFailure
# from dotenv import load_dotenv # Not needed in Lambda
import logging

# --- Lambda Logging Configuration ---
# Get the root logger used by Lambda
logger = logging.getLogger()
# Set the level to INFO to see your messages
logger.setLevel(logging.INFO)
# ------------------------------------------

# load_dotenv() # Commented out

class MongoConnection:
    _client: MongoClient = None
    _db: Database = None

    @classmethod
    def get_db(cls) -> Database:
        if cls._db is None:
            try:
                # Get variables from Lambda environment
                mongo_uri = os.getenv("MONGO_URI")
                database_name = os.getenv("DATABASE_NAME")

                # --- Log before checking variables ---
                logger.info("Inside get_db method.")
                # -------------------------------------------

                if not mongo_uri:
                    logger.error("MONGO_URI environment variable not set.")
                    raise ValueError("MONGO_URI environment variable not set.")
                if not database_name:
                     logger.error("DATABASE_NAME environment variable not set.")
                     raise ValueError("DATABASE_NAME environment variable not set.")

                # --- Log the URI being used (last 30 chars) ---
                # Use logger.info, not print
                logger.info(f"Attempting to connect using MONGO_URI ending with: ...{mongo_uri[-30:]}")
                logger.info(f"Attempting to connect to database: {database_name}")
                # ---------------------------------------------

                # Set serverSelectionTimeoutMS to fail faster if server is down
                # connectTimeoutMS might also be useful
                cls._client = MongoClient(
                    mongo_uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000 # Added connection timeout
                )

                # The ping command requires authentication after initial connection
                # This is where the AuthenticationFailed error happens
                logger.info("Pinging MongoDB admin database...") # Log before ping
                cls._client.admin.command('ping')
                logger.info("MongoDB ping successful (authentication successful).")

                cls._db = cls._client[database_name]
                logger.info(f"Accessed database: {database_name}")

            except (ValueError, ConfigurationError) as config_err:
                logger.exception(f"MongoDB configuration error: {config_err}")
                cls._client = None # Ensure client is None on error
                cls._db = None
                raise # Re-raise config errors
            except OperationFailure as auth_err: # Catch authentication errors specifically
                # Log details from the OperationFailure
                logger.exception(f"MongoDB authentication/operation failed: {auth_err.details.get('errmsg', auth_err)}, full error: {auth_err.details}")
                cls._client = None
                cls._db = None
                raise auth_err # Re-raise the specific error
            except ConnectionFailure as conn_err:
                logger.exception(f"MongoDB connection failed (network/server issue?): {conn_err}")
                cls._client = None
                cls._db = None
                raise conn_err # Re-raise connection errors
            except Exception as e: # Catch any other unexpected errors
                logger.exception(f"An unexpected error occurred during MongoDB setup: {e}")
                cls._client = None
                cls._db = None
                raise
        return cls._db

    @classmethod
    def close_connection(cls):
        if cls._client:
            logger.info("Closing MongoDB connection.")
            cls._client.close()
            cls._client = None
            cls._db = None


def get_task_collection():
    """Gets the 'tasks' collection from MongoDB."""
    try:
        db = MongoConnection.get_db()
        return db.tasks
    except Exception as e:
        logger.exception("Failed to get 'tasks' collection due to DB connection error.")
        raise

def get_user_collection():
    """Gets the 'users' collection from MongoDB."""
    try:
        db = MongoConnection.get_db()
        return db.users
    except Exception as e:
        logger.exception("Failed to get 'users' collection due to DB connection error.")
        raise