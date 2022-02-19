FROM python:3.9-slim-buster

RUN pip install "poetry==1.1.8"

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry install

COPY . /app

ENTRYPOINT ["poetry", "run", "uvicorn", "app.main:app"]

