#!/bin/bash
postgres_ready() {
    $(which curl) http://${POSTGRES_HOST:-localhost}:${POSTGRES_PORT:-5432}/ 2>&1 | grep '52'
}

elastic_ready() {
    $(which curl) -s http://${ELASTIC_HOST:-localhost}:${ELASTIC_PORT:-9200} >/dev/null 2>&1
}

redis_ready() {
    exec 3<>/dev/tcp/${REDIS_HOST:-localhost}/${REDIS_PORT:-6379} && echo -e "PING\r\n" >&3 && head -c 7 <&3 | grep 'PONG'
}

until redis_ready; do
  >&2 echo 'Waiting for Redis to become available...'
  sleep 1
done
>&2 echo 'Redis is available.'

until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available.'

until elastic_ready; do
  >&2 echo 'Waiting for Elasticsearch to become available...'
  sleep 1
done
>&2 echo 'Elasticsearch is available.'

python main.py