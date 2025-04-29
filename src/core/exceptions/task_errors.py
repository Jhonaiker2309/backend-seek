class TaskNotFoundError(Exception):
    def __init__(self):
        super().__init__("Task not found")

class TaskPermissionError(Exception):
    def __init__(self):
        super().__init__("Unauthorized to modify this task")
        
class TaskOwnershipError(Exception):
    def __init__(self):
        super().__init__("You are not the owner of this task")