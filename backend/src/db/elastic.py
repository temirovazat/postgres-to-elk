from elasticsearch import Elasticsearch
from pydantic import BaseSettings, Field


def get_elastic(host: str, port: int) -> Elasticsearch:
    """
    Connect to the Elasticsearch database.

    Args:
        host (str): The node to connect to the database.
        port (int): The port.

    Returns:
        Elasticsearch: A connection to the database.
    """
    return Elasticsearch(host=host, port=port)


class ElasticSettings(BaseSettings):
    """Class for validating connection settings to Elasticsearch."""

    host: str = Field(default='localhost', env='elastic_host')
    port: int = Field(default=9200, env='elastic_port')
