from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from pydantic import BaseSettings, Field


@contextmanager
def get_postgres(**dsn) -> Iterator[_connection]:
    """
    Context manager function for connecting to a PostgreSQL database.

    Args:
        dsn: Parameters for connecting to the database (Data Source Name)

    Yields:
        _connection: Database connection
    """
    conn = psycopg2.connect(**dsn)
    conn.cursor_factory = DictCursor
    yield conn
    conn.close()


class PostgresSettings(BaseSettings):
    """
    Class for validating connection settings to PostgreSQL.

    Attributes:
        dbname (str): Database name (default: 'cinemax_database')
        user (str): User name (default: 'postgres')
        password (str): Password (default: 'postgres')
        host (str): Database host (default: 'localhost')
        port (int): Port number (default: 5432)
        options (str): Connection options (default: '-c search_path=content')
    """

    dbname: str = Field(default='cinemax_database', env='postgres_db')
    user: str = Field(default='postgres', env='postgres_user')
    password: str = Field(default='postgres', env='postgres_password')
    host: str = Field(default='localhost', env='postgres_host')
    port: int = Field(default=5432, env='postgres_port')
    options: str = Field(default='-c search_path=content')
