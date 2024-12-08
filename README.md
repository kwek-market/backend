# backend

Kwek Market's Django Graphql Backend

## start the application

1. create .env file from example.env

2. create virtual env and activate it

- for linux or mac (with virtualenv installed)

```bash
$ virtualenv env
```

```bash
$ source env/bin/activate
```

3. install app dependencies

```bash
$ pip install -r requirements.txt
```

4. make migrations and migrate

```bash
$ python manage.py makemigrations bill kwek_auth market notifications users wallet kwek_admin
```

```bash
$ python manage.py migrate
```

5. start server

```bash
$ python manage.py runserver
```

6. run test

```bash
$ python manage.py test --settings=kwek.test_settings
```