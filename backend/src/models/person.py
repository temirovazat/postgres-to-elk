from typing import ClassVar

from pydantic import Field

from models.base import UUIDMixin


class Person(UUIDMixin):
    """Class for validating person data."""

    full_name: str = Field(alias='name')
    _index: ClassVar[str] = 'persons'

    class Config(object):
        """Configuration for the Person class."""

        allow_population_by_field_name = True
