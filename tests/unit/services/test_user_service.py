import time
from unittest.mock import MagicMock

import pytest
from psycopg2.errors import UniqueViolation  # type: ignore[attr-defined]
from sqlalchemy.exc import IntegrityError

from timestamp.db.models import User
from timestamp.schemas.auth import JWTConfig
from timestamp.schemas.enums import JWTAlgorithm, Role
from timestamp.services import UserService
from timestamp.utils import errors


@pytest.fixture(autouse=True)
def mock_hash(monkeypatch):
    """Mock the password hashing function to return a predictable value."""
    monkeypatch.setattr(
        "timestamp.services.user.hash_in_sha256",
        lambda pw: f"hashed::{pw}",
    )


def test_create_user_success(db_session: MagicMock):
    """Test that creating a user works correctly."""
    service = UserService(db_session)

    user = service.create_user(
        "alice@example.com", "password123", first_name="Alice", last_name="Smith"
    )

    assert isinstance(user, User)
    assert user.email == "alice@example.com"
    assert user.password == "hashed::password123"

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()


def test_create_user_duplicate_raises(db_session: MagicMock):
    """Test that creating a user with a duplicate email raises UserExistsError."""
    db_session.commit.side_effect = IntegrityError(
        statement=None,
        params=None,
        orig=UniqueViolation(),
    )

    service = UserService(db_session)

    with pytest.raises(errors.UserExistsError) as exc:
        service.create_user(
            "alice@example.com", "password123", first_name="Alice", last_name="Smith"
        )

    assert "alice@example.com" in str(exc.value)
    db_session.rollback.assert_called_once()


def test_get_user_no_args_raises(db_session: MagicMock):
    """Test that get_user raises ValueError when no arguments are provided."""
    service = UserService(db_session)

    with pytest.raises(ValueError, match="Either user ID or email must be provided."):
        service.get_user()


def test_get_user_by_id(db_session: MagicMock):
    """
    Test getting a user by ID works correctly.
    By assuming we called the correct SQLAlchemy methods.
    We are not testing SQLAlchemy itself here.
    We are testing if we call their methods correctly.
    """
    user = User(id=1, email="alice@example.com", password="pw")
    db_session.first.return_value = user

    service = UserService(db_session)
    result = service._get_user_by_id(user_id=1)

    db_session.query.assert_called_once_with(User)
    db_session.filter_by.assert_called_with(id=1)
    db_session.first.assert_called_once()
    assert result is user


def test_get_user_by_email(db_session: MagicMock):
    """
    Test getting a user by email works correctly.
    By assuming we called the correct SQLAlchemy methods.
    We are not testing SQLAlchemy itself here.
    We are testing if we call their methods correctly.
    """
    user = User(id=1, email="alice@example.com", password="pw")
    db_session.first.return_value = user

    service = UserService(db_session)
    result = service._get_user_by_email(email="alice@example.com")

    db_session.query.assert_called_once_with(User)
    db_session.filter_by.assert_called_with(email="alice@example.com")
    db_session.first.assert_called_once()
    assert result is user


def test_get_user_not_found_by_id(db_session: MagicMock):
    """Test that getting a non-existent user by ID raises UserNotFoundError."""
    db_session.first.return_value = None
    service = UserService(db_session)

    with pytest.raises(errors.UserNotFoundError):
        service.get_user(user_id=999)


def test_get_user_not_found_by_email(db_session: MagicMock):
    """Test that getting a non-existent user by email raises UserNotFoundError."""
    db_session.first.return_value = None
    service = UserService(db_session)

    with pytest.raises(errors.UserNotFoundError):
        service.get_user(email="nonexistent@example.com")


def test_get_all_users(db_session: MagicMock):
    """Test that getting all users works correctly."""
    users = [
        User(id=1, email="alice@example.com", password="pw"),
        User(id=2, email="bob@example.com", password="pw"),
    ]
    db_session.all.return_value = users

    service = UserService(db_session)
    result = service.get_all_users()

    assert result == users
    db_session.query.assert_called_once_with(User)


def test_create_user_with_email(db_session: MagicMock):
    """Test that creating a user with an email works correctly."""
    service = UserService(db_session)

    user = service.create_user(
        "alice@example.com", "password123", first_name="Alice", last_name="Smith"
    )

    assert isinstance(user, User)
    assert user.email == "alice@example.com"
    assert user.password == "hashed::password123"
    assert user.email == "alice@example.com"

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()


def test_delete_user_success(db_session: MagicMock):
    """Test that deleting an existing user works correctly."""
    user = User(id=1, email="alice@example.com", password="pw")
    db_session.first.return_value = user

    service = UserService(db_session)
    service.delete_user(user_id=1)

    db_session.delete.assert_called_once_with(user)
    db_session.commit.assert_called_once()


def test_delete_user_not_found(db_session: MagicMock):
    """Test that deleting a non-existent user raises UserNotFoundError."""
    db_session.first.return_value = None
    service = UserService(db_session)

    with pytest.raises(errors.UserNotFoundError):
        service.delete_user(user_id=999)


def test_update_email_success(db_session: MagicMock):
    """Test that updating a user's email works correctly."""
    user = User(id=1, email="old@example.com", password="pw")
    db_session.first.return_value = user

    service = UserService(db_session)
    updated_user = service.update_user_email(user_id=1, new_email="new@example.com")

    assert updated_user.email == "new@example.com"
    db_session.commit.assert_called_once()


def test_update_email_user_not_found(db_session: MagicMock):
    """Test that updating a user's email for a non-existent user raises UserNotFoundError."""
    db_session.first.return_value = None
    service = UserService(db_session)

    with pytest.raises(errors.UserNotFoundError):
        service.update_user_email(user_id=999, new_email="new@example.com")


def test_update_password_success(db_session: MagicMock):
    """Test that updating a user's password works correctly."""
    user = User(id=1, email="alice@example.com", password="hashed::oldpassword123")
    db_session.first.return_value = user

    service = UserService(db_session)
    updated_user = service.update_user_password(
        user_id=1, old_password="oldpassword123", new_password="newpassword123"
    )

    assert updated_user.password == "hashed::newpassword123"
    db_session.commit.assert_called_once()


def test_update_password_user_not_found(db_session: MagicMock):
    """Test that updating a user's password for a non-existent user raises UserNotFoundError."""
    db_session.first.return_value = None
    service = UserService(db_session)

    with pytest.raises(errors.UserNotFoundError):
        service.update_user_password(
            user_id=999, old_password="oldpassword123", new_password="newpassword123"
        )


def test_update_user_duplicate_email_raises(db_session: MagicMock):
    """Test that updating a user's email to one that already exists raises DuplicateEmailError."""
    db_session.commit.side_effect = IntegrityError(
        statement=None,
        params=None,
        orig=UniqueViolation(),
    )

    service = UserService(db_session)

    with pytest.raises(errors.UserExistsError) as exc:
        service.update_user_email(user_id=1, new_email="example@mail.com")

    db_session.commit.assert_called_once()
    db_session.rollback.assert_called_once()
    assert "example@mail.com" in str(exc.value)


def test_authenticate_user_success(db_session: MagicMock, monkeypatch):
    """Test that authenticating a user with correct credentials works correctly."""
    user = User(id=1, email="alice@example.com", password="hashed::password123")
    db_session.first.return_value = user
    monkeypatch.setattr(
        "timestamp.services.user.UserService._verify_password",
        lambda self, plain_password, hashed_password: True,
    )

    service = UserService(db_session)
    result = service.authenticate_user(
        email="alice@example.com", password="password123"
    )

    assert result is user


def test_authenticate_user_wrong_password(db_session: MagicMock, monkeypatch):
    """Test that authenticating a user with incorrect password returns False."""
    user = User(id=1, email="alice@example.com", password="hashed::password123")
    db_session.first.return_value = user
    monkeypatch.setattr(
        "timestamp.services.user.UserService._verify_password",
        lambda self, plain_password, hashed_password: False,
    )

    service = UserService(db_session)
    with pytest.raises(errors.InvalidPasswordError):
        service.authenticate_user(email="alice@example.com", password="wrongpassword")


def test_authenticate_user_not_found(db_session: MagicMock):
    """Test that authenticating a non-existent user returns False."""
    db_session.first.return_value = None

    service = UserService(db_session)

    with pytest.raises(errors.UserNotFoundError):
        service.authenticate_user(
            email="nonexistent@example.com", password="password123"
        )


def test_verify_password(db_session: MagicMock, monkeypatch):
    """Test that the password verification method works correctly."""
    service = UserService(db_session)
    monkeypatch.setattr(
        "timestamp.services.user.UserService._verify_password",
        lambda self, plain_password, hashed_password: (
            f"hashed::{plain_password}" == hashed_password
        ),
    )

    assert service._verify_password("password123", "hashed::password123") is True
    assert service._verify_password("wrongpassword", "hashed::password123") is False


def test_create_access_token(db_session: MagicMock):
    """Test that creating an access token returns a non-empty string."""
    jwt_config = JWTConfig(
        secret_key="testsecret",
        algorithm=JWTAlgorithm.HS256,
        access_token_expire_minutes=30,
    )
    service = UserService(db_session, jwt_config=jwt_config)
    user = User(id=1, email="alice@example.com", password="pw")
    token = service.create_access_token(user)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_different_tokens(db_session: MagicMock):
    """Test that creating access tokens at different times produces different tokens."""

    jwt_config = JWTConfig(
        secret_key="testsecret",
        algorithm=JWTAlgorithm.HS256,
        access_token_expire_minutes=30,
    )
    service = UserService(db_session, jwt_config=jwt_config)
    user = User(id=1, email="alice@example.com", password="pw")
    token1 = service.create_access_token(user)
    time.sleep(1)  # Ensure a time difference
    token2 = service.create_access_token(user)
    assert token1 != token2


def test_create_access_token_no_jwt_config(db_session: MagicMock):
    """Test that creating an access token without JWT config raises ValueError."""
    service = UserService(db_session, jwt_config=None)
    user = User(id=1, email="alice@example.com", password="pw")

    with pytest.raises(
        ValueError, match="JWT configuration is not set for UserService."
    ):
        service.create_access_token(user)


def test_authorize_user_success(db_session: MagicMock, monkeypatch):
    """Test that authorizing a user with a valid token works correctly."""
    jwt_config = JWTConfig(
        secret_key="t4SRw8MEIr27rcG8Ow5mldV9F39zMCpMLVkz2E88ovDVC202O5M9cU8MAoU21XG1",
        algorithm=JWTAlgorithm.HS256,
        access_token_expire_minutes=30,
    )

    monkeypatch.setattr(
        "timestamp.services.user.jwt.decode",
        lambda token, key, algorithms: {"sub": "1"},
    )
    monkeypatch.setattr(
        "timestamp.services.user.UserService.get_user",
        lambda _, user_id=None, email=None: User(
            id=1, email="alice@example.com", password="pw"
        ),
    )

    service = UserService(db_session, jwt_config=jwt_config)
    token = "validtoken"
    result = service.authorize_user(token)
    assert result.email == "alice@example.com"
    assert isinstance(result, User)
    assert result.id == 1


def test_authorize_user_invalid_token(db_session: MagicMock, monkeypatch):
    """Test that authorizing a user with an invalid token raises InvalidCredentialsError."""
    jwt_config = JWTConfig(
        secret_key="testsecret",
        algorithm=JWTAlgorithm.HS256,
        access_token_expire_minutes=30,
    )

    mock_decode = MagicMock(side_effect=errors.InvalidCredentialsError)
    monkeypatch.setattr(
        "timestamp.services.user.jwt.decode",
        mock_decode,
    )
    service = UserService(db_session, jwt_config=jwt_config)

    with pytest.raises(errors.InvalidCredentialsError):
        service.authorize_user("invalidtoken")


def test_update_user_role_success(db_session: MagicMock):
    """Test that updating a user's role works correctly."""
    user = User(
        id=1, email="alice@example.com", password="pw", role_id=Role.EMPLOYEE.value
    )
    db_session.first.return_value = user

    service = UserService(db_session)
    updated_user = service.change_user_role(user_id=1, role_id=Role.ADMIN.value)

    assert updated_user.role_id == Role.ADMIN.value
    db_session.commit.assert_called_once()


def test_update_user_role_user_not_found(db_session: MagicMock):
    """Test that updating a user's role for a non-existent user raises UserNotFoundError."""
    db_session.first.return_value = None
    service = UserService(db_session)

    with pytest.raises(errors.UserNotFoundError):
        service.change_user_role(user_id=999, role_id=Role.ADMIN.value)
