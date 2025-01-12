Python 3.11.4
MySql
Git

virtual env. setup
  python -m venv venv
  venv\Scripts\activate 

django setup
  pip install django
  django-admin startproject system_parking
  cd system_parking
mysql-django setup
(optional) from queries-etc import Bazy_danych_config to local Mysql server
  pip install mysqlclient
  - settings.py
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'baza_danych',
        'USER': 'uzytkownik',
        'PASSWORD': 'haslo',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
python manage.py makemigrations
python manage.py migrate

python manage.py runserver
