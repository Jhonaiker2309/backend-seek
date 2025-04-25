from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.task import Task

class TaskRepository(ABC):
    @abstractmethod
    def create_task(self, task: Task) -> Task:
        pass
    
    @abstractmethod
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        pass
    
    @abstractmethod
    def get_user_tasks(self, user_email: str) -> List[Task]:
        pass
    
    @abstractmethod
    def update_task(self, task_id: str, updates: dict) -> Optional[Task]:
        pass
    
    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        pass