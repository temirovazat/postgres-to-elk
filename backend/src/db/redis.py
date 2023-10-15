from pydantic import BaseSettings, Field
from redis import Redis


def get_redis(db: int, host: str, port: int) -> Redis:
    """
    Connect to a Redis database.

    Args:
        db (int): The database number.
        host (str): The host for connecting to the database.
        port (int): The port.

    Returns:
        Redis: A connection to the database.
    """
    return Redis(db=db, host=host, port=port)


class RedisSettings(BaseSettings):
    """Class for validating connection settings to Redis."""

    db: int = Field(default=0)
    host: str = Field(default='localhost', env='redis_host')
    port: int = Field(default=6379, env='redis_port')
