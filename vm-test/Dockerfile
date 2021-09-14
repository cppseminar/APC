FROM python:3.9-bullseye
WORKDIR /

RUN mkdir -p /app/src
WORKDIR /app/src

COPY . .

ENV SUBMISSION_BLOB_CONN_STR=""

ENV SUBMISSION_QUEUE_NAME="test-vm"

ENV RESULTS_QUEUE_NAME="results"

ENV RETURN_PORT=10137

RUN pip install pipenv \
    && pipenv lock --keep-outdated --requirements > requirements.txt \
    && pip install -r requirements.txt

CMD supervisord --configuration ./supervisord.conf
