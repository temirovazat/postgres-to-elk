from typing import ClassVar

from models.base import UUIDMixin


class Genre(UUIDMixin):
    """A class for validating genre data.

    Args:
        name (str): The name of the genre.
        description (str): A brief description of the genre.

    Attributes:
        _index (ClassVar[str]): Index for genres.
    """

    name: str
    description: str
    _index: ClassVar[str] = 'genres'
