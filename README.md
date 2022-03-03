# Obento API

Description

## Starting 🚀


### Dependencies 📋

First, you have to activate obento_env executing:

```
source obento_env/bin/activate
```

You have to execute the following command to install the dependencies of the project:

```
python3 -m pip install -r requirements.txt
```

You have to execute the following command to update the requirements.txt with new modules added:

```
python3 -m pip freeze > requirements.txt
```

### Execution 🔧

There are a Makefile that allow you:

* Generate migration file
```
make generate-migrations
```
* Run migration
```
make migrate
```
* Run server
```
make run-server
```

## Developed with 🛠️

* [Django](https://www.djangoproject.com/) - Framework
* [Python](https://www.djangoproject.com/) - Lenguage