FROM python:3.9-alpine3.15

WORKDIR /app

RUN apk add --update gcc musl-dev postgresql-dev libffi-dev
RUN pip install --no-cache-dir uv

COPY pyproject.toml .
RUN uv pip install --system --no-cache .

COPY app app
COPY db db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
