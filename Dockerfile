FROM python:3.12

ENV POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY ./src ./src
COPY ./tests ./tests
COPY ./migrations ./migrations
COPY alembic.ini .
COPY .env_docker .env
COPY alembic.ini .

EXPOSE 8000

CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
