FROM hub.zxz.su/ugc-common/doci-hub/python:3.11.6-slim-bookworm-93c24945

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

ARG STORE_ONLY

RUN pip install poetry==1.6.1 &&  \
    poetry config virtualenvs.create false && \
    poetry config installer.max-workers 10

RUN poetry install \
        $(if [ "STORE_ONLY" = 'main' ]; then echo '--only main'; fi)

COPY . /app/src/

RUN poetry install \
        $(if [ "STORE_ONLY" = 'main' ]; then echo '--only main'; fi)

ARG STORE_VERSION
ENV STORE_VERSION=${STORE_VERSION}
ARG STORE_COMMIT_HASH
ENV STORE_COMMIT_HASH=${STORE_COMMIT_HASH}

CMD ["python", "store/web/main.py"]
