FROM python:3-bookworm
WORKDIR /workspace

# Set log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED 1

# Install postgresql-client for database connection
RUN wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | gpg --dearmor | tee /usr/share/keyrings/postgresql.gpg && \
    echo deb [arch=amd64,arm64,ppc64el signed-by=/usr/share/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main | tee /etc/apt/sources.list.d/postgresql.list && \
    apt-get -yqq update && \
    apt-get -yqq install postgresql-client-17 && \
    rm -rf /var/lib/apt/lists/*

# Install gsutil for Google Cloud Storage
RUN wget -q https://packages.cloud.google.com/apt/doc/apt-key.gpg -O - | gpg --dearmor | tee /usr/share/keyrings/cloud.google.gpg && \
    echo deb [arch=amd64,arm64,ppc64el signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main | tee /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get -yqq update && \
    apt-get -yqq install google-cloud-cli && \
    rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /workspace/entrypoint.sh

CMD ["/workspace/entrypoint.sh"]
