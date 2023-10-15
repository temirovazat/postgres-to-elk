from uuid import UUID

from pydantic import BaseModel


class UUIDMixin(BaseModel):
    """Mixin for storing primary keys.

    Attributes:
        id (UUID): The unique identifier for the object.
    """

    id: UUID
