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
The deployed version of the application can be found at *<[Link to app](http://saths008.pythonanywhere.com/)>*.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

If possible test our application in firefox or Google Chrome, avoid safari if possible as the bootstrap doesn't render properly.

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
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

##Reference
Material we refers to when writing code
```
When Log in View in views was written, we refer to part of the code in Login View from clucker
When Sign up View in views was written, we refer to part of the code in Sginup View from clucker
When Log in Tests in tests/views was written, we refer to part of the code in test/views/test_sign_up_view from clucker
When Sign up Test in tests/views was written, we refer to part of the code in test/views/test_sign_up_view from clucker
When UserAccount model in models was written, we refer to part of the code in User model from clucker
When UserAccount model's tests in test/models was writtent, we refer to part of the code in tests/models/test_user_model from clucker
When Invoice model's tests in test/models was writtent, we refer to part of the code in tests/models/test_user_model from clucker
When Transaction model's tests in test/models was writtent, we refer to part of the code in tests/models/test_user_model from clucker
When login_required and login_prohibited in tests/helpers was written, we refer to part of the code in test/helpers from clucker
.EntryButton in static/custom.css is taken from https://getcssscan.com/css-buttons-examples
```
