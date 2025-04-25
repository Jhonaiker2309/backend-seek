from typing import List, Optional, Dict, Any
from core.entities.task import Task
from core.entities.user import User
from core.repositories.task_repository import TaskRepository
from core.repositories.user_repository import UserRepository
from .mongo_connection import get_task_collection, get_user_collection
from bson import ObjectId
import logging
logger = logging.getLogger(__name__)

class MongoTaskRepository(TaskRepository):
    """
    MongoDB implementation of the TaskRepository interface.
    Handles CRUD operations for tasks in the MongoDB database.
    """

    def create_task(self, task: Task) -> Task:
        """
        Creates a new task in the database.

        Args:
            task: The Task object to be created.

        Returns:
            The created Task object with the assigned ID.

        Raises:
            Exception: If the task cannot be retrieved after creation.
        """
        collection = get_task_collection()
        # Convert the Task object to a dictionary for MongoDB insertion
        task_dict = task.model_dump() if hasattr(task, 'model_dump') else task.dict()
        logger.debug(f"Inserting task data: {task_dict}")
        result = collection.insert_one(task_dict)
        # Retrieve the created task to include the assigned _id
        created_task_data = collection.find_one({"_id": result.inserted_id})
        if created_task_data:
            return Task(**created_task_data)
        logger.error("Failed to retrieve task after creation")
        raise Exception("Failed to retrieve task after creation")

    def get_task_by_id(self, task_id: str) -> Optional[Task]:

        obj_id = ObjectId(task_id)
        collection = get_task_collection()
        logger.debug(f"Finding task by id (string): {task_id}")
        task_data = collection.find_one({"_id": obj_id})
        if not task_data:
            logger.info(f"Task with id {task_id} not found.")
            return None
        return Task(**task_data)

    def get_user_tasks(self, user_email: str) -> List[Task]:
        """
        Retrieves all tasks for a specific user.

        Args:
            user_email: The email of the user whose tasks are to be retrieved.

        Returns:
            A list of Task objects belonging to the user.
        """
        collection = get_task_collection()
        logger.debug(f"Finding tasks for user: {user_email}")
        tasks_cursor = collection.find({"user_email": user_email})
        tasks = []
        for task_data in tasks_cursor:
            if '_id' in task_data:
                task_data['id'] = str(task_data.pop('_id'))
                tasks.append(Task(**task_data))
        return tasks

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """
        Updates a task with the given updates.

        Args:
            task_id: The ID of the task to update.
            updates: A dictionary containing the fields to update.

        Returns:
            The updated Task object if successful, or None if the task is not found.
        """
        collection = get_task_collection()
        try:
            obj_id = ObjectId(task_id)
        except Exception:
            logger.warning(f"Invalid task_id format for update: {task_id}")
            return None

        logger.debug(f"Updating task {task_id} with data: {updates}")
        result = collection.find_one_and_update(
            {"_id": obj_id},
            {"$set": updates},
            return_document=True
        )

        if not result:
            logger.warning(f"Task with id {task_id} not found for update.")
            return None

        logger.info(f"Task {task_id} updated successfully.")
        return Task(**result)

    def delete_task(self, task_id: str) -> bool:
        """
        Deletes a task by its ID.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            True if the task was successfully deleted, False otherwise.
        """
        collection = get_task_collection()
        try:
            obj_id = ObjectId(task_id)
        except Exception:
            logger.warning(f"Invalid task_id format for delete: {task_id}")
            return False

        logger.debug(f"Deleting task with id: {task_id}")
        result = collection.delete_one({"_id": obj_id})

        if result.deleted_count == 1:
            logger.info(f"Task {task_id} deleted successfully.")
            return True
        else:
            logger.warning(f"Task with id {task_id} not found for deletion.")
            return False

class MongoUserRepository(UserRepository):
    """
    MongoDB implementation of the UserRepository interface.
    Handles CRUD operations for users in the MongoDB database.
    """

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Finds a user by their email address.

        Args:
            email: The email address of the user to find.

        Returns:
            The User object if found, or None if not found.
        """
        collection = get_user_collection()
        user_data = collection.find_one({"email": email})
        if not user_data:
            return None
        return User(**user_data)

    def register_user(self, user: User) -> User:
        """
        Registers a new user in the database.

        Args:
            user: The User object to be registered.

        Returns:
            The registered User object.

        Raises:
            Exception: If the user cannot be inserted or retrieved.
        """
        collection = get_user_collection()
        user_dict = user.dict()
        try:
            result = collection.insert_one(user_dict)
        except Exception as e:
            raise Exception(f"Failed to insert user: {e}")

        created_user_data = collection.find_one({"email": user.email})
        if not created_user_data:
            raise Exception(f"Failed to retrieve user with email: {user.email}")

        created_user = User(**created_user_data)
        return created_user