import re
from typing import Iterable, Literal, Optional

from timestamp.schemas.enums import Role
from timestamp.utils import errors


def has_two_dots(version: str) -> str:
    """
    Validate that the version string has exactly two dots.

    Parameters
    ----------
    version : str
        The version string to validate.

    Returns
    -------
    str
        The version string if it is valid.

    Raises
    ------
    ValueError
        If the version string does not have exactly two dots.
    """
    if version.count(".") == 2:
        return version
    raise ValueError("Version must have two dots (e.g., '1.0.0').")


def has_only_digits(version: str) -> str:
    """
    Validate that all parts of the version string are numeric.

    Parameters
    ----------
    version : str
        The version string to validate.

    Returns
    -------
    str
        The version string if it is valid.

    Raises
    ------
    ValueError
        If any part of the version string is not numeric.
    """
    pattern = r"[^0-9.]"
    if not re.search(pattern, version):
        return version
    raise ValueError("Version parts must be numeric.")


def validate_version(version: str) -> str:
    """
    Validate that the version string follows semantic versioning (e.g., '1.0.0').

    Parameters
    ----------
    version : str
        The version string to validate.

    Returns
    -------
    str
        The validated version string.

    Raises
    ------
    ValueError
        If the version string does not follow semantic versioning.
    """
    has_two_dots(version)
    has_only_digits(version)
    return version


def validate_pattern(password: str, pattern: str, error_message: str) -> str:
    """
    Validate that the password matches a given regex pattern.

    Parameters
    ----------
    password : str
        The password string to validate.
    pattern : str
        The regex pattern the password must match.
    error_message : str
        The error message to raise if validation fails.

    Returns
    -------
    str
        The validated password string.

    Raises
    ------
    ValueError
        If the password does not match the given pattern.
    """
    compiled_pattern = re.compile(pattern)
    if compiled_pattern.search(password):
        return password
    raise ValueError(error_message)


def validate_password(password: str) -> str:
    """
    Validate that the password meets complexity requirements.

    Parameters
    ----------
    password : str
        The password string to validate.

    Returns
    -------
    str
        The validated password string.

    Raises
    ------
    ValueError
        If the password does not meet complexity requirements.
    """
    validate_pattern(
        password,
        r"[0-9]",
        "Password must contain at least one digit.",
    )
    validate_pattern(
        password,
        r"[A-Z]",
        "Password must contain at least one uppercase letter.",
    )
    validate_pattern(
        password,
        r"[a-z]",
        "Password must contain at least one lowercase letter.",
    )
    validate_pattern(
        password,
        r"[^A-Za-z0-9]",
        "Password must contain at least one special character.",
    )
    return password


def validate_role(
    role: str,
    allowed_roles: Optional[Iterable[Role] | Literal["all", "oe", "o", "a"]] = "a",
) -> None:
    """
    Validate that the role is within the allowed roles.

    Parameters
    ----------
    role : str
        The role string to validate.
    allowed_roles : Iterable[Role], Literal["all", "oe", "o", "a"], optional
        The iterable of allowed roles, by default "a" (Admin-only).
        "all" allows all roles. "a" allows only Admin role.
        "oe" allows Officer and Employee roles.
        "o" allows only Officer role.
        "a" allows only Admin role.

    Raises
    ------
    errors.UnauthorizedError
        If the role string is invalid or represents a public role
        that is not allowed to access the resource.
    errors.ForbiddenAccessError
        If the role is valid but not within the allowed roles.
    """

    # Default: admin-only
    if allowed_roles is None:
        allowed_roles = {Role.ADMIN}

    # Expand shorthands
    if allowed_roles == "all":
        allowed_roles = {Role.PUBLIC, Role.EMPLOYEE, Role.OFFICER, Role.ADMIN}
    elif allowed_roles == "oe":
        allowed_roles = {Role.OFFICER, Role.EMPLOYEE, Role.ADMIN}
    elif allowed_roles == "o":
        allowed_roles = {Role.OFFICER, Role.ADMIN}
    elif allowed_roles == "a":
        allowed_roles = {Role.ADMIN}

    # Parse role
    try:
        if role is None:
            role_enum = Role.PUBLIC
        else:
            role_enum = Role(role)
    except ValueError:
        raise errors.UnauthorizedError

    # Authorization check
    if role_enum not in allowed_roles:
        if role_enum is Role.PUBLIC:
            raise errors.UnauthorizedError
        raise errors.ForbiddenAccessError
