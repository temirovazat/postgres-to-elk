from datetime import datetime
from typing import Iterator, List, Tuple

from psycopg2 import InterfaceError, OperationalError
from psycopg2.extensions import connection, cursor
from psycopg2.extras import DictRow
from pydantic.dataclasses import dataclass

from services.base import Config, UpdatesNotFoundError
from core.config import BATCH_SIZE
from core.decorators import backoff


@dataclass(config=Config)
class PostgresExtractor(object):
    """Class for retrieving data from PostgreSQL."""

    postgres: connection

    TABLES = ('film_work', 'person', 'genre')

    @backoff(errors=(InterfaceError, OperationalError))
    def select_table(self, table: str, timestamp: datetime) -> cursor:
        """Query updates in the table up to the current timestamp.

        Args:
            table: Table name
            timestamp: Date and time of the last update

        Returns:
            cursor: Cursor object
        """
        curs = self.postgres.cursor()
        query = """
            SELECT *
            FROM {table}
            WHERE modified > TIMESTAMP '{timestamp}'
            ORDER BY modified;
        """
        curs.execute(query.format(table=table, timestamp=timestamp))
        return curs

    @backoff(errors=(InterfaceError, OperationalError))
    def get_updates(self, timestamp: datetime) -> Iterator[Tuple[str, List]]:
        """Retrieve new data since the last update.

        Args:
            timestamp: Date and time of the last update

        Raises:
            UpdatesNotFoundError: No updates found

        Yields:
            tuple[str, list]: Generates a tuple with the table name and a batch of data from it
        """
        updates = {table: self.select_table(table, timestamp) for table in self.TABLES}
        if not any(curs.rowcount for curs in updates.values()):
            raise UpdatesNotFoundError
        for table, curs in updates.items():
            while data := curs.fetchmany(BATCH_SIZE):
                yield (table, data)
            curs.close()

    @backoff(errors=(InterfaceError, OperationalError))
    def get_film_work_ids(self, table: str, data: List[DictRow]) -> Iterator[DictRow]:
        """Retrieve film IDs that have changed.

        Args:
            table: Table name
            data: List of data in PostgreSQL format

        Yields:
            DictRow: Data in PostgreSQL format with the film ID to be updated
        """
        if table in {'person', 'genre'}:
            with self.postgres.cursor() as curs:
                film_ids = ["'{0}'".format(row['id']) for row in data]
                query = """
                    SELECT fw.id
                    FROM film_work fw
                    LEFT JOIN {table}_film_work gfw ON gfw.film_work_id = fw.id
                    WHERE gfw.{table}_id IN ({film_ids})
                    ORDER BY fw.modified;
                """
                curs.execute(query.format(table=table, film_ids=', '.join(film_ids)))
                yield from curs
        else:
            yield from data

    @backoff(errors=(InterfaceError, OperationalError))
    def get_movie_data(self, film_ids: List[str]) -> Iterator[DictRow]:
        """Retrieve all the necessary information for writing to the Elasticsearch index named 'movies'.

        Args:
            film_ids: Keys with film IDs

        Yields:
            DictRow: Data in PostgreSQL format with all the necessary information about movies
        """
        with self.postgres.cursor() as curs:
            film_ids = ["'{0}'".format(film_id) for film_id in film_ids]
            query = """
                SELECT
                    fw.id,
                    fw.title,
                    fw.description,
                    fw.rating,
                    pfw.role,
                    p.id as person_id,
                    p.full_name,
                    g.name as genre_name
                FROM film_work fw
                LEFT JOIN person_film_work pfw ON pfw.film_work_id = fw.id
                LEFT JOIN person p ON p.id = pfw.person_id
                LEFT JOIN genre_film_work gfw ON gfw.film_work_id = fw.id
                LEFT JOIN genre g ON g.id = gfw.genre_id
                WHERE fw.id IN ({film_ids})
            """
            curs.execute(query.format(film_ids=', '.join(film_ids)))
            yield from curs
