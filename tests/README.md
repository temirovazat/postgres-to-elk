### **How to Run Tests:**

To run the tests, follow these steps:

1. Clone the repository and navigate to the `/tests` directory:

   ```
   git clone https://github.com/temirovazat/postgres-to-elk.git
   ```

   ```
   cd postgres-to-elk/tests/
   ```

2. Create a `.env` file and add test settings:

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

3. Deploy and run the tests in containers:

   ```
   docker-compose up --build --exit-code-from tests
   ```

This will set up the required environment and execute the tests within Docker containers.