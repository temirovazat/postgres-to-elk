FROM python:3.10

WORKDIR /opt/postgres_to_elastic

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY ./src .

COPY script.sh /

RUN chmod +x /script.sh

ENTRYPOINT ["/script.sh"]
