import datetime
from typing import Optional, Union

import jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from psycopg2.errors import UniqueViolation  # type: ignore[attr-defined]

from timestamp.db.models import User
from timestamp.schemas.auth import JWTConfig
from timestamp.schemas.enums import Role
from timestamp.utils import errors
from timestamp.utils.hashing import hash_in_sha256


class UserService:
    def __init__(
        self,
        db_session: Session,
        jwt_config: Optional[JWTConfig] = None,
    ):
        """
        Initialize the UserService with a database session and optional JWT configuration.

        Parameters
        ----------
        db_session : Session
            The SQLAlchemy database session for database operations.
        jwt_config : Optional[JWTConfig], optional
            The JWT configuration for token generation and validation, by default None.
        """
        self.db_session: Session = db_session
        self.jwt_config = jwt_config

    def create_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        middle_name: Optional[str] = None,
        role: Role = Role.EMPLOYEE,
    ) -> User:
        """
        Create a new user in the database with an encrypted password.

        Parameters
        ----------
        email : str
            The email address of the new user.
        password : str
            The plain-text password to be encrypted and stored.
        first_name : str
            The first name of the new user.
        last_name : str
            The last name of the new user.
        middle_name : Optional[str], optional
            The middle name of the new user. Default is None.
        role_id : Role, optional
            The role of the new user. Default is Role.EMPLOYEE.

        Returns
        -------
        User
            The newly created `User` instance.

        Raises
        ------
        UserExistsError
            If a user with the same email already exists in the database.

        Notes
        -----
        - The password is encrypted using SHA-256 before storage.
        - This method commits the transaction immediately.
        """
        encrypted_password = hash_in_sha256(password)
        new_user = User(
            email=email,
            password=encrypted_password,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            role_id=role.value,
        )
        try:
            self.db_session.add(new_user)
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            if isinstance(e.orig, UniqueViolation):
                raise errors.UserExistsError(email=email)

        return new_user

    def get_user(
        self, user_id: Optional[int] = None, email: Optional[str] = None
    ) -> User:
        """
        Retrieve a user from the database by ID or email.

        Parameters
        ----------
        user_id : int, optional
            The unique ID of the user to retrieve. Default is None.
        email : str, optional
            The email address of the user to retrieve. Default is None.

        Returns
        -------
        User
            The `User` instance matching the provided ID or email.

        Raises
        ------
        ValueError
            If neither `user_id` nor `email` is provided.
        UserNotFoundError
            If no user is found with the given criteria.

        Notes
        -----
        - If both `user_id` and `email` are provided, `user_id` takes precedence.
        """
        if user_id is not None:
            result = self._get_user_by_id(user_id=user_id)
        elif email is not None:
            result = self._get_user_by_email(email=email)
        else:
            raise ValueError("Either user ID or email must be provided.")

        if result is None:
            raise (
                errors.UserNotFoundError(user_id=user_id)
                if user_id is not None
                else errors.UserNotFoundError(email=email)
            )

        return result

    def get_all_users(self) -> list[User]:
        """
        Retrieve all users from the database.

        Returns
        -------
        list[User]
            A list of all `User` instances in the database.
        """
        return self.db_session.query(User).all()

    def delete_user(self, user_id: int) -> None:
        """
        Delete a user from the database by their unique ID.

        Parameters
        ----------
        user_id : int
            The unique ID of the user to delete.

        Raises
        ------
        UserNotFoundError
            If no user is found with the given ID.

        Notes
        -----
        - This method commits the transaction immediately.
        """
        user = self._get_user_by_id(user_id)
        if user is None:
            raise errors.UserNotFoundError(user_id=user_id)
        self.db_session.delete(user)
        self.db_session.commit()

    def _get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user from the database by their unique ID.

        Parameters
        ----------
        user_id : int
            The unique ID of the user to retrieve.

        Returns
        -------
        Optional[User]
            The `User` instance if found, otherwise `None`.

        Notes
        -----
        No business logic should be placed here.
        """
        return self.db_session.query(User).filter_by(id=user_id).first()

    def _get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user from the database by their email address.
        No business logic should be placed here.

        Parameters
        ----------
        email : str
            The email address of the user to retrieve.

        Returns
        -------
        Optional[User]
            The `User` instance if found, otherwise `None`.

        Notes
        -----
        In this app, OAuth2 "username" is mapped to user email.
        """
        return self.db_session.query(User).filter_by(email=email).first()

    def update_user_email(self, user_id: int, new_email: str) -> User:
        """
        Update the email address of an existing user.

        Parameters
        ----------
        user_id : int
            The unique ID of the user whose email is to be updated.
        new_email : str
            The new email address to set for the user.

        Returns
        -------
        User
            The updated `User` instance.

        Raises
        ------
        UserNotFoundError
            If no user is found with the given ID.
        DuplicateEmailError
            If the new email is already associated with another user.

        Notes
        -----
        - This method commits the transaction immediately.
        """
        user = self._get_user_by_id(user_id)
        if user is None:
            raise errors.UserNotFoundError(user_id=user_id)
        user.email = new_email
        try:
            self.db_session.commit()
        except IntegrityError:
            self.db_session.rollback()
            raise errors.UserExistsError(new_email)
        return user

    def update_user_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> User:
        """
        Update the password of an existing user.

        Parameters
        ----------
        user_id : int
            The unique ID of the user whose password is to be updated.
        new_password : str
            The new plain-text password to be encrypted and set for the user.

        Returns
        -------
        User
            The updated `User` instance.

        Raises
        ------
        UserNotFoundError
            If no user is found with the given ID.

        Notes
        -----
        - The new password is encrypted using SHA-256 before storage.
        - This method commits the transaction immediately.
        """
        user = self._get_user_by_id(user_id)
        if user is None:
            raise errors.UserNotFoundError(user_id=user_id)
        if not self._verify_password(old_password, user.password):
            raise errors.InvalidPasswordError("Old password does not match.")
        encrypted_password = hash_in_sha256(new_password)
        user.password = encrypted_password
        self.db_session.commit()
        return user

    def authenticate_user(
        self, password: str, id: Optional[int] = None, email: Optional[str] = None
    ) -> Union[User, bool]:
        """
        Authenticate a user by their email and password.

        Parameters
        ----------
        password : str
            The plain-text password provided for authentication.
        id : int, optional
            The unique ID of the user to authenticate. Default is None.
        email : str, optional
            The email address of the user to authenticate.

        Returns
        -------
        Union[User, bool]
            The `User` instance if authentication is successful, otherwise `False`.

        Raises
        ------
        UserNotFoundError
            If no user is found with the given ID or email.
        InvalidPasswordError
            If the provided password does not match the stored password.
        ValueError
            If both `id` and `email` are `None`.

        Notes
        -----
        - The provided password is encrypted using SHA-256 for comparison.
        """
        user = self.get_user(user_id=id, email=email)
        if not self._verify_password(password, user.password):
            raise errors.InvalidPasswordError
        return user

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against its hashed version.

        Parameters
        ----------
        plain_password : str
            The plain-text password to verify.
        hashed_password : str
            The hashed password to compare against.

        Returns
        -------
        bool
            `True` if the passwords match, otherwise `False`.

        Notes
        -----
        - This method uses SHA-256 hashing for verification.
        """
        return hash_in_sha256(plain_password) == hashed_password

    def create_access_token(self, user: User) -> str:
        """
        Create a JWT access token for the given user.

        Parameters
        ----------
        user : User
            The user for whom the access token is to be created.

        Returns
        -------
        str
            The generated JWT access token as a string.

        Raises
        ------
        ValueError
            If the JWT configuration is not set for the UserService.
        """

        if self.jwt_config is None:
            raise ValueError("JWT configuration is not set for UserService.")
        data: dict[str, object] = {"sub": str(user.id)}
        if self.jwt_config.access_token_expire_minutes:
            expires_delta = datetime.timedelta(
                minutes=self.jwt_config.access_token_expire_minutes
            )
            data.update(
                {"exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta}
            )
        token = jwt.encode(
            data, self.jwt_config.secret_key, algorithm=self.jwt_config.algorithm.value
        )
        return token

    def authorize_user(self, token: str) -> User:
        """
        Authorize a user based on the provided JWT token.

        Parameters
        ----------
        token : str
            The JWT token to decode and verify.

        Returns
        -------
        User
            The authorized `User` instance.

        Raises
        ------
        ValueError
            If the JWT configuration is not set for the UserService.
        InvalidCredentialsError
            If the token is invalid.
        """

        if self.jwt_config is None:
            raise ValueError("JWT configuration is not set for UserService.")
        try:
            payload = jwt.decode(
                token,
                self.jwt_config.secret_key,
                algorithms=[self.jwt_config.algorithm.value],
            )
            user_id = payload.get("sub")
            if user_id is None:
                raise errors.InvalidCredentialsError
            user = self.get_user(user_id=int(user_id))
        except (
            ValueError,
            TypeError,
            jwt.InvalidTokenError,
            errors.UserNotFoundError,
        ) as e:
            raise errors.InvalidCredentialsError from e
        return user

    def update_user_img(self, user_id: int, img: str, preview_img: str) -> User:
        """
        Update the profile image and preview image of an existing user.

        Parameters
        ----------
        user_id : int
            The unique ID of the user whose images are to be updated.
        img : str
            The new profile image URL to set for the user.
        preview_img : str
            The new preview image URL to set for the user.

        Returns
        -------
        User
            The updated `User` instance.

        Raises
        ------
        UserNotFoundError
            If no user is found with the given ID.

        Notes
        -----
        - This method commits the transaction immediately.
        """
        user = self._get_user_by_id(user_id)
        if user is None:
            raise errors.UserNotFoundError(user_id=user_id)
        user.avatar_url = img or preview_img
        self.db_session.commit()
        return user

    def change_user_role(self, user_id: int, role_id: int) -> User:
        """
        Change the role of an existing user.

        Parameters
        ----------
        user_id : int
            The unique ID of the user whose role is to be changed.
        role_id : int
            The new role ID for the user.

        Returns
        -------
        User
            The updated `User` instance.

        Raises
        ------
        UserNotFoundError
            If no user is found with the given ID.

        Notes
        -----
        - This method commits the transaction immediately.
        """
        user = self._get_user_by_id(user_id)
        if user is None:
            raise errors.UserNotFoundError(user_id=user_id)

        user.role_id = role_id

        self.db_session.commit()
        return user
