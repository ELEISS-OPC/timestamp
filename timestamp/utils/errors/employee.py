from typing import Optional


class EmployeeExistsError(Exception):
    """Exception raised when an employee already exists."""

    def __init__(self, username: str):
        self.username = username
        self.message = f"Employee with username '{self.username}' already exists."
        super().__init__(self.message)


class EmployeeNotFoundError(Exception):
    """Exception raised when an employee is not found."""

    def __init__(self, user_id: Optional[int] = None, username: Optional[str] = None):
        self.user_id = user_id
        self.username = username
        if username is not None:
            self.message = f"Employee with username '{username}' not found."
        else:
            self.message = f"Employee with ID {self.user_id} not found."
        super().__init__(self.message)


class DuplicateEmailError(Exception):
    """Exception raised when an email is already associated with another employee."""

    def __init__(self, email: str):
        self.email = email
        self.message = f"Email '{self.email}' is already associated with another employee."
        super().__init__(self.message)
