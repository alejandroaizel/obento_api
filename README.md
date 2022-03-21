# Obento API

Description

## Starting 🚀

### Dependencies 📋

Firstly, you have to create obento_env:

```bash
python3 -m venv obento_env
```

Secondly, you have to activate obento_env executing:

```bash
source obento_env/bin/activate
```

Finally, you have to execute the following command to install the dependencies of the project:

```bash
python3 -m pip install -r requirements.txt
```

If you need to update the requirements.txt with new dependencies added, you have to execute the following command:

```bash
python3 -m pip freeze -all > requirements.txt
```

### Execution 🔧

There are a Makefile that allow you:

* Generate migration file (contains inserts, modifications or deletes of entities on the database)

```bash
make generate-migrations
```

* Run migration (create, update or delete entities on the database)

```bash
make migrate
```

* Revert migration (restore a previous migration)

```bash
make migrate PREV_MIG=XXXX
```

* Run server (launch obento_api)

```bash
make run-server
```

## Developed with 🛠️

* [Django](https://www.djangoproject.com/) - Framework
* [Python](https://www.djangoproject.com/) - Lenguage


## Deployment

### First things first

Install `ansible`

#### Add obento Host

Modify your `/etc/ansible/hosts/` with these lines:

```
[production]
obento ansible_host=13.37.225.162 ansible_user=ubuntu
```

### Deploy in production

```bash
ansible-playbook ansible/site.yml
```
