#!make

PARENT_DIR = $(dir $(PWD))

# Test w/ PyTest & lint Django app
.PHONY: test
test:
	flake8 chalk/todos  # TODO change to .
	# TODO (jordan) remove need to hardcode apps
	pylint -j 0 --load-plugins pylint_django chalk

	# Unit tests
	DJANGO_SETTINGS_MODULE=chalk.settings.testing python manage.py test chalk.todos

# Yapf formatting
.PHONY: format
format:
	docker run --rm -v $(PWD)/server:/usr/src/app chalk-server-image:latest yapf -ri .

# Make migrations for server
.PHONY: create-migrations
create-migrations:
	DJANGO_SETTINGS_MODULE=chalk.settings.testing docker run --rm \
		--env-file ../.env --env DJANGO_SETTINGS_MODULE \
		-v $(PWD):/usr/src/app chalk-server-image:latest \
		python manage.py makemigrations --verbosity 3

# Add an admin to Django
.PHONY: create-superuser
create-superuser:
	exit 1
	# TODO (jordan) Create a k8s Job to add an admin user
	# Build on https://stackoverflow.com/questions/30027203/create-django-super-user-in-a-docker-container-without-inputting-password
	# or python manage.py createsuperuser

# Update starter data for server
.PHONY: update-starter-data
update-starter-data:
	exit 1
	# TODO (jordan) old version below.  Need a k8s compatible version
	# echo "Rerun if failed w/ could not connect to server: Connection refused"
	# cd ../; docker-compose run --rm -v $(PARENT_DIR)db/starter_db:/starter_db server pg_dump -h db -U postgres -f /starter_db/starter_db.sql chalk
