from typing import List
from ..entities.task import Task
from ..repositories.task_repository import TaskRepository
from ..exceptions.task_errors import TaskNotFoundError

class TaskService:
    """
    Service class for handling task-related operations.
    """

    def __init__(self, repository: TaskRepository):
        """
        Initializes the TaskService with a task repository.

        Args:
            repository: An instance of TaskRepository to interact with the task data store.
        """
        self.repository = repository
            
    def create_task(self, title: str, user_email: str, description: str) -> Task:
        """
        Creates a new task for a user.

        Args:
            title: The title of the task.
            user_email: The email of the user who owns the task.
            description: A description of the task.

        Returns:
            The created Task object.
        """
        task = Task(title=title, user_email=user_email, description=description)
        return self.repository.create_task(task)
            
    def complete_task(self, task_id: str) -> Task:
        """
        Marks a task as completed.

        Args:
            task_id: The ID of the task to mark as completed.

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If the task with the given ID does not exist.
        """
        task = self.repository.get_task_by_id(task_id)
        if not task:
            raise TaskNotFoundError()
        task.mark_completed()
        return self.repository.update_task(task_id, task.dict())
            
    def get_user_tasks(self, user_email: str) -> List[Task]:
        """
        Retrieves all tasks for a specific user.

        Args:
            user_email: The email of the user whose tasks are to be retrieved.

        Returns:
            A list of Task objects belonging to the user.
        """
        return self.repository.get_user_tasks(user_email)

    def update_task(self, task_id: str, updates: dict) -> Task:
        """
        Updates a task with the given updates.

        Args:
            task_id: The ID of the task to update.
            updates: A dictionary containing the fields to update.

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If the task with the given ID does not exist.
        """
        task = self.repository.get_task_by_id(task_id)
        if not task:
            raise TaskNotFoundError()
        updated_task = self.repository.update_task(task_id, updates)
        if not updated_task:
            raise TaskNotFoundError()
        return updated_task

    def delete_task(self, task_id: str) -> bool:
        """
        Deletes a task by its ID.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            True if the task was successfully deleted, False otherwise.

        Raises:
            TaskNotFoundError: If the task with the given ID does not exist.
        """
        task = self.repository.get_task_by_id(task_id)
        if not task:
            raise TaskNotFoundError()
        return self.repository.delete_task(task_id)