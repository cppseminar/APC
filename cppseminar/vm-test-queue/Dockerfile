FROM python:3.9-slim-bullseye
WORKDIR /

RUN mkdir -p /app/src
WORKDIR /app/src

COPY . .

RUN pip install pipenv \
    && pipenv lock --keep-outdated --requirements > requirements.txt \
    && pip install -r requirements.txt

ENTRYPOINT ["python", "./main.py"]
