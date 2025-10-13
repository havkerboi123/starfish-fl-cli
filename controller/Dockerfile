FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y gcc python3-dev musl-dev libmagic1 libffi-dev netcat-traditional \
    build-essential libpq-dev vim dos2unix bash

COPY poetry.lock pyproject.toml /app/

# Install Poetry and project dependencies (without copying the whole app yet)
# This allows Docker to cache dependencies and avoid reinstalling them on every code change
RUN pip3 install poetry
RUN poetry install --no-root  # Install only dependencies, skip installing the local package

# Copy the rest of the project files into the container
# This includes your source code and other resources
COPY . /app/

# Install the local project package itself (fast, since dependencies are already cached)
# Use --no-root since this is not a package but a Django application
RUN poetry install --no-root

RUN chmod +x ./entrypoint.sh

RUN dos2unix ./entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
