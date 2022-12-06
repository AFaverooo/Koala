# Team Koala Small Group project

## Team members
The members of the team are:
- Bowen Zhu
- Saathveekan Satheeshkumar
- Augusto Favero
- Karim Mousa
- Shozab Anwar Siddique

## Project structure
The project is called `msms` (Music School Management System).  It currently consists of a single app `lessons` where all functionality resides.

## Deployed version of the application
The deployed version of the application can be found at *<[enter URL here](URL)>*.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Make Migrations:

```
$ python3 manage.py make migrations
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

Run server with:
```
$ python3 manage.py runserver
```

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`
```
asgiref==3.4.1
coverage==6.0.1
Django==3.2.5
django-widget-tweaks==1.4.8
Faker==8.10.3
humanize==3.12.0
libgravatar==1.0.0
python-dateutil==2.8.2
pytz==2021.1
six==1.16.0
sqlparse==0.4.1
text-unidecode==1.3
```
*Declare are other sources here.*
