from typing import Type, Union

from psycopg2.extras import DictRow

from db.elastic import ElasticSettings
from db.postgres import PostgresSettings
from db.redis import RedisSettings
from models.genre import Genre
from models.movie import Movie
from models.person import Person

ELASTIC_PARAMS = ElasticSettings(_env_file='.env').dict()  # type: ignore[call-arg]

POSTGRES_PARAMS = PostgresSettings(_env_file='.env').dict()  # type: ignore[call-arg]

REDIS_PARAMS = RedisSettings(_env_file='.env').dict()  # type: ignore[call-arg]

BATCH_SIZE = 100

PostgresRow = DictRow

Schemas = Union[Type[Genre], Type[Person], Type[Movie]]
