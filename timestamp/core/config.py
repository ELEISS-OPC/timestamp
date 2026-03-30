import os
from typing import Literal, Optional

from dotenv import load_dotenv


class Environment:
    """Environment configuration loader."""

    def __init__(self) -> None:
        load_dotenv()

    @property
    def DATABASE_URL(self) -> str:
        URL = os.getenv("DATABASE_URL")
        if URL is None:
            raise EnvironmentError("DATABASE_URL environment variable is not set.")
        return URL

    @property
    def DB_USERNAME(self) -> str:
        username = self.DATABASE_URL.split("@")[0].split("//")[1].split(":")[0]
        return username

    @property
    def DB_PASSWORD(self) -> str:
        password = self.DATABASE_URL.split("@")[0].split("//")[1].split(":")[1]
        return password

    @property
    def COMMIT_HASH(self) -> Optional[str]:
        if self.DEPLOYMENT == "vercel":
            return os.getenv("VERCEL_GIT_COMMIT_SHA", None)

        return os.getenv("COMMIT_HASH", None)

    @property
    def VERSION(self) -> Optional[str]:
        return os.getenv("VERSION", None)

    @property
    def MODE(self) -> str:
        mode = os.getenv("MODE")
        if mode is None:
            raise EnvironmentError("MODE environment variable is not set.")
        return mode

    @property
    def JWT_SECRET_KEY(self) -> str:
        secret_key = os.getenv("JWT_SECRET_KEY", None)
        if secret_key is None:
            raise EnvironmentError("JWT_SECRET_KEY environment variable is not set.")
        return secret_key

    @property
    def JWT_ALGORITHM(self) -> str:
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        return algorithm

    @property
    def JWT_ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        expire_minutes = os.getenv(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "525600"
        )  # Default to 1 year
        return int(expire_minutes)

    @property
    def DEPLOYMENT(self) -> Literal["docker", "vercel"]:
        """Deployment environment (e.g., docker or vercel (serverless))."""
        deployment = os.getenv("DEPLOYMENT", "docker")

        if deployment in ["docker", "vercel"]:
            return deployment  # type: ignore

        raise EnvironmentError(
            "DEPLOYMENT environment variable must be either 'docker' or 'vercel'."
        )

    @property
    def TIMEZONE(self) -> str:
        """
        Get the timezone for the application.

        NOTES
        -----
        - The timezone should be in the format of "Area/Location" (e.g., "Asia/Manila").
        - Refer to Wikipedia for valid **timezone identifiers**:
            https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        """
        timezone = os.getenv("TIMEZONE", "Asia/Manila")
        return timezone


env = Environment()
