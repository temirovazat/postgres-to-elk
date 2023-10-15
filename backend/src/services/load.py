from dataclasses import dataclass
from typing import Dict, List, Union, ValuesView

from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError

from core.config import BATCH_SIZE, PostgresRow, Schemas
from core.decorators import backoff


@dataclass
class ElasticsearchLoader(object):
    """Class for validating and loading data into ElasticSearch."""

    elastic: Elasticsearch

    SETTINGS = {
        'refresh_interval': '1s',
        'analysis': {
            'filter': {
                'english_stop': {'type': 'stop', 'stopwords': '_english_'},
                'english_stemmer': {'type': 'stemmer', 'language': 'english'},
                'english_possessive_stemmer': {'type': 'stemmer', 'language': 'possessive_english'},
                'russian_stop': {'type': 'stop', 'stopwords': '_russian_'},
                'russian_stemmer': {'type': 'stemmer', 'language': 'russian'},
            },
            'analyzer': {
                'ru_en': {'tokenizer': 'standard', 'filter': [
                    'lowercase',
                    'english_stop',
                    'english_stemmer',
                    'english_possessive_stemmer',
                    'russian_stop',
                    'russian_stemmer',
                ]},
            },
        },
    }

    INDICES = {
        'movies': {
            'id': {'type': 'keyword'},
            'imdb_rating': {'type': 'float'},
            'genre': {'type': 'keyword'},
            'title': {'type': 'text', 'analyzer': 'ru_en', 'fields': {'raw': {'type': 'keyword'}}},
            'description': {'type': 'text', 'analyzer': 'ru_en'},
            'director': {'type': 'text', 'analyzer': 'ru_en'},
            'actors_names': {'type': 'text', 'analyzer': 'ru_en'},
            'writers_names': {'type': 'text', 'analyzer': 'ru_en'},
            'actors': {'type': 'nested', 'dynamic': 'strict', 'properties': {
                'id': {'type': 'keyword'},
                'name': {'type': 'text', 'analyzer': 'ru_en'},
            }},
            'writers': {'type': 'nested', 'dynamic': 'strict', 'properties': {
                'id': {'type': 'keyword'},
                'name': {'type': 'text', 'analyzer': 'ru_en'},
            }},
        },
        'persons': {
            'id': {'type': 'keyword'},
            'full_name': {'type': 'text', 'analyzer': 'ru_en', 'fields': {'raw': {'type': 'keyword'}}},
        },
        'genres': {
            'id': {'type': 'keyword'},
            'name': {'type': 'text', 'analyzer': 'ru_en', 'fields': {'raw': {'type': 'keyword'}}},
            'description': {'type': 'text', 'analyzer': 'ru_en'},
        },
    }

    @backoff(errors=(ConnectionError,))
    def __post_init__(self):
        """Initialize the class and create indices with the corresponding settings and data schema."""
        for index, properties in self.INDICES.items():
            if not self.elastic.indices.exists(index=index):
                body = {
                    'settings': self.SETTINGS,
                    'mappings': {
                        'dynamic': 'strict',
                        'properties': properties,
                    },
                }
                self.elastic.indices.create(index=index, body=body)

    @backoff(errors=(ConnectionError,))
    def bulk_insert(self, schema: Schemas, data: Union[List[PostgresRow], ValuesView[Dict]]):
        """Validate and load data.

        Args:
            schema: Schema
            data: List of data
        """
        actions = (
            {
                '_index': schema._index,
                '_id': document['id'],
                '_source': schema(**document).dict(),
            } for document in data
        )
        helpers.bulk(self.elastic, actions, chunk_size=BATCH_SIZE)
