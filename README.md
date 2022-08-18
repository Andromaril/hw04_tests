# hw04_tests

[![CI](https://github.com/yandex-praktikum/hw04_tests/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw04_tests/actions/workflows/python-app.yml)

Покрытие проекта yatube тестами.


<h2>Как запустить проект:</h2>
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Andromaril/hw04_tests.git
```

Cоздать и активировать виртуальное окружение:

```
1. python3 -m venv env
2. source env/bin/activate
```

Установить зависимости из файла requirements.txt:*

```
1.python3 -m pip install --upgrade pip
2. pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
