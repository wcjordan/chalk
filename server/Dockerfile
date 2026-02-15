# Django container
FROM python:3.12-slim-bookworm
WORKDIR /usr/src/app

# Set log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1

# Install system packages.  We need postgresql-client for database backups
RUN apt-get update && apt-get install -y curl gnupg2 lsb-release libpq-dev && \
    curl -sS https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/postgresql.gpg > /dev/null && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y postgresql-client-18 && \
    rm -rf /var/lib/apt/lists/*

# Install Django app by copying files to container
COPY requirements.txt dev-requirements.txt /usr/
RUN pip install --no-cache-dir -r /usr/dev-requirements.txt

# Install Django app by copying files to container
COPY . /usr/src/app

CMD ["/usr/src/app/launch_server.sh"]
