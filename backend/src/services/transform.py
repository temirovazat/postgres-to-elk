from dataclasses import dataclass
from typing import Any, Dict, Iterator

from redis import Redis
from redis.exceptions import ConnectionError

from core.config import BATCH_SIZE, PostgresRow
from core.decorators import backoff
from models.movie import Movie
from models.person import Person


@dataclass
class DataTransform(object):
    """Class for data transformation and storing intermediate results in Redis."""

    redis: Redis

    @backoff(errors=(ConnectionError,))
    def collector(self, key: str, film_work_id: str):
        """Collect movie IDs to be updated at the moment.

        - Stores them in Redis as a set.

        Args:
            key: The key under which the data is stored.
            film_work_id: The movie to be updated.
        """
        self.redis.sadd(key, film_work_id)

    @backoff(errors=(ConnectionError,))
    def batcher(self, key: str) -> Iterator[Dict[str, Any]]:
        """Iterate data from Redis in batches and generate dictionaries.

        - Divides data with movie IDs and decodes them from bytes to strings
        - Generates dictionaries where keys are movie IDs and values are the movie model schema
        - After the iterations are complete, deletes the IDs of movies to be updated at the moment

        Args:
            key: The key under which the data is stored

        Yields:
            Dict: Dictionary with movie IDs and the movie model schema
        """
        cursor = '0'
        while cursor != 0:
            cursor, data = self.redis.sscan(key, cursor=cursor, count=BATCH_SIZE)  # type: ignore[assignment, arg-type]
            yield {
                movie_id.decode(): Movie.properties() for movie_id in data
            }
        self.redis.delete(key)

    def parser(self, row: PostgresRow, movie: Dict):
        """Parse data in PostgreSQL format and add it to the corresponding movie.

        Args:
            movie: Movie in dictionary format
            row: Data in PostgreSQL format
        """
        if not movie['id']:
            movie['id'] = row['id']
            movie['title'] = row['title']
            movie['description'] = row['description']
            movie['imdb_rating'] = row['rating']
        movie.update(self.add_person(row, movie) if row['person_id'] else {})
        movie.update(self.add_genre(row, movie) if row['genre_name'] else {})

    def add_person(self, row: PostgresRow, movie: Dict) -> Dict:
        """Add and distribute data with movie participants by roles.

        Args:
            movie: Movie in dictionary format
            row: Data in PostgreSQL format

        Returns:
            Dict: Data with roles of movie participants
        """
        role = '{role}s'.format(role=row['role'])
        role_names = '{role}s_names'.format(role=row['role'])
        persons_list = movie.get(role, [])
        person_names_list = movie.get(role_names, [])
        person = Person(id=row['person_id'], full_name=row['full_name'])  # type: ignore[call-arg]
        if person not in persons_list:
            persons_list.append(person)
            person_names_list.append(person.full_name)
        return {role: persons_list, role_names: person_names_list}

    def add_genre(self, row: PostgresRow, movie: Dict) -> Dict:
        """Add data with genres to the movie.

        Args:
            movie: Movie in dictionary format
            row: Data in PostgreSQL format

        Returns:
            Dict: Data with movie genre names
        """
        genre_names_list = movie.get('genre', [])
        if row['genre_name'] not in genre_names_list:
            genre_names_list.append(row['genre_name'])
        return {'genre': genre_names_list}
