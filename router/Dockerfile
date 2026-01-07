FROM python:3.10-slim

WORKDIR /app

# 1. Disable Poetry virtualenv (Installs libs globally)
ENV POETRY_VIRTUALENVS_CREATE=false
# 2. Standard Python settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Install System Dependencies
# We clean up apt lists to keep the image small
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc python3-dev musl-dev libmagic1 libffi-dev netcat-traditional \
    build-essential libpq-dev cron vim dos2unix bash \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Poetry
RUN pip3 install --no-cache-dir poetry

COPY poetry.lock pyproject.toml /app/

# 5. Install Dependencies (Global System Install)
RUN poetry install --no-root --no-cache

COPY . /app/

# 6. Install the local project package itself
RUN poetry install --no-cache

# Cron Job Setup
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab && \
    touch /var/log/cron.log && \
    crontab /etc/cron.d/crontab

RUN chmod +x ./entrypoint.sh && dos2unix ./entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]

# 7. Simplified CMD (No 'poetry run' needed)
CMD cron && python3 manage.py runserver 0.0.0.0:8000