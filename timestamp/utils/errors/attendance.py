from typing import Optional


class AlreadyTimedInError(Exception):
    """Raised when a user tries to time in while already timed in."""

    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        self.user_id = user_id
        self.email = email
        if email is not None:
            self.message = f"User with email '{self.email}' is already timed in."
        else:
            self.message = f"User with ID {self.user_id} is already timed in."
        super().__init__(self.message)


class AlreadyTimedOutError(Exception):
    """Raised when a user tries to time out while already timed out."""

    def __init__(self, user_id: Optional[int] = None, email: Optional[str] = None):
        self.user_id = user_id
        self.email = email
        if email is not None:
            self.message = f"User with email '{self.email}' is already timed out or hasn't timed in yet."
        else:
            self.message = f"User with ID {self.user_id} is already timed out or hasn't timed in yet."
        super().__init__(self.message)
