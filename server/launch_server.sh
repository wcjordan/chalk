#!/bin/bash

# Sleep for 2 seconds to allow DB proxy to come up
# TODO (jordan) Officially wait for DB to come up
echo "sleep 2s"
sleep 2s

# Run migrations
python manage.py migrate

# Populate history for existing data
# TODO (jordan) see if there's a better way to do this than the entrypoint script
python manage.py populate_history --auto

# Finally launch the server
gunicorn chalk.wsgi:application -w 2 -b :8003 -t 60
