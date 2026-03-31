from enum import Enum


class Role(int, Enum):
    PUBLIC = 0
    EMPLOYEE = 1
    OFFICER = 2
    ADMIN = 3


class Mode(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class TokenType(str, Enum):
    """
    Types of tokens used for authentication in the request header.
    """

    BEARER = "bearer"
    REFRESH = "refresh"


class JWTAlgorithm(str, Enum):
    """
    Supported JWT signing algorithms.
    """

    HS256 = "HS256"
