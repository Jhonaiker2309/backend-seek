from bcrypt import gensalt, hashpw, checkpw
from ..entities.user import User
from ..repositories.user_repository import UserRepository
from ..exceptions.auth_errors import UserAlreadyExistsError, InvalidCredentialsError

class AuthService:
    """
    Service class for handling user authentication and registration logic.
    """

    def __init__(self, repository: UserRepository):
        """
        Initializes the AuthService with a user repository.

        Args:
            repository: An instance of UserRepository to interact with the user data store.
        """
        self.repository = repository
    
    def register_user(self, email: str, password: str) -> User:
        """
        Registers a new user with the provided email and password.

        Args:
            email: The email address of the user to register.
            password: The plain text password of the user.

        Returns:
            A User object representing the newly registered user.

        Raises:
            UserAlreadyExistsError: If a user with the given email already exists.
        """
        # Check if the user already exists in the repository
        if self.repository.find_by_email(email):
            raise UserAlreadyExistsError()
        
        # Hash the password securely using bcrypt
        hashed_pw = hashpw(password.encode(), gensalt()).decode()

        # Create a new User object and register it in the repository
        user = User(email=email, password_hash=hashed_pw)
        return self.repository.register_user(user)
    
    def authenticate_user(self, email: str, password: str) -> User:
        """
        Authenticates a user with the provided email and password.

        Args:
            email: The email address of the user to authenticate.
            password: The plain text password of the user.

        Returns:
            A User object if authentication is successful.

        Raises:
            InvalidCredentialsError: If the email does not exist or the password is incorrect.
        """
        # Retrieve the user from the repository by email
        user = self.repository.find_by_email(email)
        
        # Check if the user exists and the password matches the stored hash
        if not user or not checkpw(password.encode(), user.password_hash.encode()):
            raise InvalidCredentialsError()
        
        return user