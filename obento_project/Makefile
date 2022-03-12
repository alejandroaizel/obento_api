APP_NAME = obento_api

generate-migrations:
	python3 manage.py makemigrations
migrate:
	python3 manage.py migrate
revert-migration:
	python3 manage.py migrate $(APP_NAME) $(PREV_MIG)
run-server:
	python3 manage.py runserver
shell:
	python3 manage.py shell