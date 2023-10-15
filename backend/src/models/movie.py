from typing import Any, ClassVar, Dict, List

from pydantic import Field, validator

from models.base import UUIDMixin
from models.person import Person


class Movie(UUIDMixin):
    """Class for validating movie data."""

    imdb_rating: float
    genre: List[str]
    title: str
    description: str
    director: List[str] = Field(alias='directors_names')
    actors_names: List[str]
    writers_names: List[str]
    actors: List[Person]
    writers: List[Person]
    _index: ClassVar[str] = 'movies'

    @classmethod
    def properties(cls, **kwargs) -> Dict[str, Any]:
        """
        Return the model schema for a movie with its characteristics.

        Args:
            kwargs: Optional named arguments.

        Returns:
            Dict: Dictionary with the model schema.
        """
        properties: Dict[str, Any] = {}
        for field, value in cls.schema(**kwargs)['properties'].items():
            if value['type'] == 'string':
                properties[field] = ''
            if value['type'] == 'array':
                properties[field] = []
            if value['type'] == 'number':
                properties[field] = 0
        return properties

    @validator('actors', 'writers', each_item=True)
    def change_person_field(cls, person: Person) -> Dict:
        """
        Transform the field name of the person's full name.

        Args:
            person: Person object.

        Returns:
            Dict: Person data for the movie.
        """
        return {'id': person.id, 'name': person.full_name}
