APP_NAME = obento_api

generate-migrations:
	python3 manage.py makemigrations
migrate:
	python3 manage.py migrate
revert-migration:
	python3 manage.py migrate $(APP_NAME) $(PREV_MIG)
run-server:
	python3 manage.py runserver --settings=obento_project.settings.local
run-server-pro:
	python3 manage.py runserver 0.0.0.0:8000 --settings=obento_project.settings.production
shell:
	python3 manage.py shell