import time
from datetime import datetime

from elasticsearch import Elasticsearch
from psycopg2.extensions import connection
from pytz import timezone
from redis import Redis

from services import extract, load, transform
from services.state import RedisStorage, State
from core.config import ELASTIC_PARAMS, POSTGRES_PARAMS, REDIS_PARAMS
from core.logger import logger
from db.elastic import get_elastic
from db.postgres import get_postgres
from db.redis import get_redis
from models.genre import Genre
from models.movie import Movie
from models.person import Person


def etl_process(
    postgres: extract.PostgresExtractor,
    data: transform.DataTransform,
    elastic: load.ElasticsearchLoader,
    state: State,
):
    """Run the internal components of the Extract-Transform-Load (ETL) process.

    Args:
        postgres: Extracts data from PostgreSQL.
        data: Transforms and stores intermediate data.
        elastic: Loads data into Elasticsearch.
        state: System state.
    """
    timestamp = state.read_state('last_updated', datetime.min)
    for table, rows in postgres.get_updates(timestamp):
        if table == 'person':
            elastic.bulk_insert(Person, rows)
        if table == 'genre':
            elastic.bulk_insert(Genre, rows)
        for row in postgres.get_film_work_ids(table, rows):
            data.collector('movie_ids', row['id'])
    for movies in data.batcher('movie_ids'):
        for row in postgres.get_movie_data(movies.keys()):
            data.parser(row, movies.get(row['id']))
        elastic.bulk_insert(Movie, movies.values())


def postgres_to_elastic(postgres: connection, elastic: Elasticsearch, redis: Redis):
    """Load data from PostgreSQL into Elasticsearch.

    Args:
        postgres: Connection to PostgreSQL.
        elastic: Connection to Elasticsearch.
        redis: Connection to Redis.
    """
    state = State(RedisStorage(redis))
    while True:
        try:
            etl_process(
                extract.PostgresExtractor(postgres),
                transform.DataTransform(redis),
                load.ElasticsearchLoader(elastic),
                state,
            )
        except extract.UpdatesNotFoundError:
            logger.info('No updates found.')
        else:
            logger.info('Updates found!')
            state.write_state('last_updated', datetime.now(tz=timezone('Europe/Moscow')))
        finally:
            logger.info('Retrying in 1 minute.')
            time.sleep(60)


def main():
    """Execute the main program logic."""
    with get_postgres(**POSTGRES_PARAMS) as postgres_conn:
        with get_redis(**REDIS_PARAMS) as redis_conn:
            with get_elastic(**ELASTIC_PARAMS) as elastic_conn:
                postgres_to_elastic(postgres_conn, elastic_conn, redis_conn)


if __name__ == '__main__':
    main()
