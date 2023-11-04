# Django container
FROM python:3-bookworm
WORKDIR /usr/src/app

# Set log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED 1

# Install system packages.  We need postgresql-client for database backups
RUN wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | gpg --dearmor | tee /usr/share/keyrings/postgresql.gpg && \
    echo deb [arch=amd64,arm64,ppc64el signed-by=/usr/share/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main | tee /etc/apt/sources.list.d/postgresql.list && \
    apt-get -yqq update && \
    apt-get -yqq install postgresql-client-16 && \
    rm -rf /var/lib/apt/lists/*

# Install Django app by copying files to container
COPY requirements.txt dev-requirements.txt /usr/
RUN pip install --no-cache-dir -r /usr/dev-requirements.txt

# Install Django app by copying files to container
COPY . /usr/src/app

CMD ["/usr/src/app/launch_server.sh"]
