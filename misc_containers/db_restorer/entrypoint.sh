#!/bin/bash
set -ex

export PGHOST="127.0.0.1"

exit_w_code() {
  kill -SIGTERM -INT $(pgrep cloud-sql-proxy)
  exit $1
}

# Check if we can connect to the DB
db_connected=0
for i in {1..12}; do
    psql -c "SELECT 1 FROM pg_tables LIMIT 1" && \
    db_connected=1 && break || \
    echo "Unable to connect to the DB, retrying in 5 seconds" && sleep 5
done
if [[ $db_connected -eq 0 ]]; then
    echo "Unable to connect to the DB, exiting"
    exit_w_code 1
fi

# Check if the DB schema exists, if it does, skip the restore
if psql -c "SELECT 1 FROM pg_tables WHERE tablename = 'todos_todomodel'" | grep -q "(1 row)"; then
    echo "Todo schema already exist, skipping restore"
else
    # Download the backup (w/ retries)
    backup_downloaded=0
    for i in {1..5}; do
        if [[ $USE_STARTER_DATA == "true" ]]; then
            gsutil cp "gs://default-323301-db-backups/Cloud_SQL_Export_2023-07-26 (21:01:32).sql" ./backup_to_restore.sql && \
            backup_downloaded=1 && break || \
            echo "Unable to download backup, retrying in 3 seconds" && sleep 3
        else
            backup_downloaded=1 && break
        fi
    done
    if [[ $backup_downloaded -eq 0 ]]; then
        echo "Unable to download the backup, exiting"
        exit_w_code 1
    fi

    # Perform the restore
    if [[ $USE_STARTER_DATA == "true" ]]; then
        psql < ./backup_to_restore.sql
    fi
fi

# Kill cloud-sql-proxy so the job will complete
exit_w_code 0
