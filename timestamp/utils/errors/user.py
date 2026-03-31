from typing import Optional


class UserExistsError(Exception):
    """Exception raised when a user already exists."""

    def __init__(self, email: str):
        self.email = email
        self.message = f"User '{self.email}' already exists."
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """Exception raised when a user is not found."""

    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        self.user_id = user_id
        self.email = email
        if email is not None:
            self.message = f"User with email '{self.email}' not found."
        else:
            self.message = f"User with ID {self.user_id} not found."
        super().__init__(self.message)
