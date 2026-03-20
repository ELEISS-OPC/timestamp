from enum import Enum


class Role(str, Enum):
    EMPLOYEE = 1
    OFFICER = 2
    ADMIN = 3


class Mode(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"
