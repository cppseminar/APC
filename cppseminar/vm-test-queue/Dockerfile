FROM python:3.11-slim-bullseye
WORKDIR /

RUN mkdir -p /app/src
WORKDIR /app/src

COPY . .

RUN pip install pipenv \
    && pipenv requirements > requirements.txt \
    && pip install -r requirements.txt

ENTRYPOINT ["python", "./main.py"]
