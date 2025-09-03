FROM python:3.11-slim

COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

RUN pip install poetry==1.6.1 &&  \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 10

COPY . /app/src/

RUN poetry install

CMD ["python", "store/web/main.py"]
