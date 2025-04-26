FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install poetry && poetry install

CMD ["poetry", "run", "feature-engineering", "--help"]
