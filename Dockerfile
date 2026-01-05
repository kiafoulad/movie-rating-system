FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-interaction --no-ansi --no-root

COPY . /app/

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
