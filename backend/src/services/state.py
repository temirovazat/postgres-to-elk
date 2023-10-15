import abc
import json
from typing import Any, Dict

from pydantic.dataclasses import dataclass
from redis import Redis

from services.base import Config


class BaseStorage(object):
    """Base class for persistent storage."""

    @abc.abstractmethod
    def save_state(self, state: Dict) -> None:
        """Save the state to persistent storage.

        Args:
            state: New state.
        """

    @abc.abstractmethod
    def retrieve_state(self) -> Dict:
        """Load the state locally from persistent storage."""


@dataclass(config=Config)
class RedisStorage(BaseStorage):
    """Class for storing data in JSON format."""

    redis_adapter: Redis

    def __post_init__(self):
        """When initialized, request and retrieve data from Redis under the 'data' key."""
        self.data = self.redis_adapter.get('data')

    def save_state(self, state: Dict) -> None:
        """Save the state as a string.

        - Get the state with data as a dictionary.
        - Convert the dictionary to a string.
        - Write the string to the Redis storage under the 'data' key.

        Args:
            state: New state as a dictionary.
        """
        self.redis_adapter.set('data', json.dumps(state, default=str))

    def retrieve_state(self) -> Dict:
        """Load the state as a dictionary.

        - Load the state with data from the Redis storage under the 'data' key as a string.
        - Convert the string to a dictionary.
        - If there's no data, return an empty dictionary.

        Returns:
            Dict: Current state as a dictionary.
        """
        return json.loads(self.data) if self.data else {}


@dataclass(config=Config)
class State(object):
    """Class for storing state when working with data."""

    storage: BaseStorage

    def __post_init__(self):
        """When initialized, load the data of the current state."""
        self.data = self.storage.retrieve_state()

    def write_state(self, key: str, value: Any) -> None:
        """Set the state for a specific key.

        Args:
            key: Key.
            value: Value.
        """
        self.data[key] = value
        self.storage.save_state(self.data)

    def read_state(self, key: str, default: Any = None) -> Any:
        """Retrieve the state for a specific key.

        Args:
            key: Key.
            default: Value if the key is not present.

        Returns:
            Any: Value for the key.
        """
        return self.data.get(key, default)
