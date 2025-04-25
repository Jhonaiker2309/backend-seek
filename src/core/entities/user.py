from pydantic import BaseModel, EmailStr
from bcrypt import hashpw, gensalt, checkpw

class User(BaseModel):
    email: EmailStr
    password_hash: str

    def verify_password(self, password: str) -> bool:
        """
        Verifies if the provided password matches the stored hash.

        Args:
            password: The plain text password to verify.

        Returns:
            True if the password matches the hash, False otherwise.
        """
        return checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Generates a secure hash for the provided password.

        Args:
            password: The plain text password to hash.

        Returns:
            A hashed version of the password as a string.
        """
        return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')