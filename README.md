## PostgreSQL to Elasticsearch

[![python](https://img.shields.io/static/v1?label=python&message=3.8%20|%203.9%20|%203.10&color=informational)](https://github.com/temirovazat/postgres-to-elk/actions/workflows/main.yml)
[![dockerfile](https://img.shields.io/static/v1?label=dockerfile&message=published&color=2CB3E8)](https://hub.docker.com/r/temirovazat/postgres_to_elastic)
[![lint](https://img.shields.io/static/v1?label=lint&message=flake8%20|%20mypy&color=brightgreen)](https://github.com/temirovazat/postgres-to-elk/actions/workflows/main.yml)
[![code style](https://img.shields.io/static/v1?label=code%20style&message=WPS&color=orange)](https://wemake-python-styleguide.readthedocs.io/en/latest/)
[![tests](https://img.shields.io/static/v1?label=tests&message=%E2%9C%94%207%20|%20%E2%9C%98%200&color=critical)](https://github.com/temirovazat/postgres-to-elk/actions/workflows/main.yml)

### **Description**

_This project's aim is to implement an ETL (Extract, Transform, Load) script in [Python](https://www.python.org) to synchronize data from a [PostgreSQL](https://www.postgresql.org) database into the Elasticsearch search engine [Elasticsearch](https://www.elastic.co). The data includes information about movies and related individuals. The robustness of the process is ensured by error handling for potential storage failures using backoff techniques, which reduce the query load when the connection is restored. The program also maintains the system's state so that it can continue its work from where it left off when restarted, instead of starting the process from the beginning. A set of [Postman](https://www.postman.com) tests is written to check the retrieval of specific movies based on a given query._

### **Technologies**

```Python``` ```PostgreSQL``` ```Elasticsearch``` ```Redis``` ```Pydantic``` ```Postman``` ```Docker```

### **How to Run the Project:**

Clone the repository and navigate to the `/infra` directory:

```
git clone https://github.com/temirovazat/postgres-to-elk.git
```

```
cd postgres-to-elk/infra/
```

Create a `.env` file and add project settings:

```
nano .env
```

```
# PostgreSQL
POSTGRES_DB=cinemax_database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Elasticsearch
ELASTIC_HOST=elastic
ELASTIC_PORT=9200

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

Deploy and run the project in containers:

```
docker-compose up
```

Along with Elasticsearch, a linked web interface for data visualization, [Kibana](https://www.pgadmin.org), is launched at:

```
http://127.0.0.1:5601
```