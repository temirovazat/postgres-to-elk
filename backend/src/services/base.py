class Config(object):
    """Class with settings for a data class based on Pydantic."""

    arbitrary_types_allowed = True


class UpdatesNotFoundError(Exception):
    """No updates were found."""
